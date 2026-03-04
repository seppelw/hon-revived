from __future__ import annotations

import logging
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Any

from homeassistant.components.switch import SwitchEntityDescription, SwitchEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import callback
from homeassistant.helpers.entity import EntityCategory
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.core import HomeAssistant
from pyhon.parameter.base import HonParameter
from pyhon.parameter.range import HonParameterRange

from .const import DOMAIN
from .entity import HonEntity
from .util import unique_entities

_LOGGER = logging.getLogger(__name__)


@dataclass(frozen=True)
class HonControlSwitchEntityDescription(SwitchEntityDescription):
    turn_on_key: str = ""
    turn_off_key: str = ""


@dataclass(frozen=True)
class HonSwitchEntityDescription(SwitchEntityDescription):
    pass


@dataclass(frozen=True)
class HonConfigSwitchEntityDescription(SwitchEntityDescription):
    entity_category: EntityCategory = EntityCategory.CONFIG


@dataclass(frozen=True, kw_only=True)
class HonDeviceAttributeSwitchEntityDescription(SwitchEntityDescription):
    """Description for attribute-based hOn switches (e.g. for heat pumps)."""
    turn_on_value: str | int = "1"
    turn_off_value: str | int = "0"


SWITCHES: dict[str, tuple[SwitchEntityDescription, ...]] = {
    "AW": (
        HonDeviceAttributeSwitchEntityDescription(
            key="onOffStatus",
            name="Power",
            icon="mdi:power",
            turn_on_value="1",
            turn_off_value="0",
            translation_key="power_switch",
        ),
        HonDeviceAttributeSwitchEntityDescription(
            key="quietMode1",
            name="Quiet Mode",
            icon="mdi:volume-mute",
            turn_on_value="1",
            turn_off_value="0",
            translation_key="quiet_mode",
        ),
        HonDeviceAttributeSwitchEntityDescription(
            key="ecoMode",
            name="Eco Mode",
            icon="mdi:leaf",
            turn_on_value="1",
            turn_off_value="0",
            translation_key="eco_mode",
        ),
        HonDeviceAttributeSwitchEntityDescription(
            key="fastDhw",
            name="Fast DHW",
            icon="mdi:water-boost",
            turn_on_value="1",
            turn_off_value="0",
            translation_key="fast_dhw",
        ),
    ),
    "WM": (
        HonControlSwitchEntityDescription(
            key="delayStatus",
            name="Delay Status",
            icon="mdi:timer-check",
            turn_on_key="startProgram",
            turn_off_key="stopProgram",
        ),
    ),
    "TD": (
        HonControlSwitchEntityDescription(
            key="delayStatus",
            name="Delay Status",
            icon="mdi:timer-check",
            turn_on_key="startProgram",
            turn_off_key="stopProgram",
        ),
    ),
    "OV": (
        HonControlSwitchEntityDescription(
            key="delayStatus",
            name="Delay Status",
            icon="mdi:timer-check",
            turn_on_key="startProgram",
            turn_off_key="stopProgram",
        ),
    ),
    "DW": (
        HonControlSwitchEntityDescription(
            key="delayStatus",
            name="Delay Status",
            icon="mdi:timer-check",
            turn_on_key="startProgram",
            turn_off_key="stopProgram",
        ),
    ),
    "AC": (
        HonSwitchEntityDescription(
            key="onOffStatus",
            name="Power",
            icon="mdi:power",
        ),
        HonSwitchEntityDescription(
            key="screenDisplayStatus",
            name="Display",
            icon="mdi:monitor",
        ),
        HonSwitchEntityDescription(
            key="echoStatus",
            name="Eco Mode",
            icon="mdi:leaf",
        ),
    ),
    "HO": (
        HonSwitchEntityDescription(
            key="onOffStatus",
            name="Power",
            icon="mdi:power",
        ),
        HonSwitchEntityDescription(
            key="lightStatus",
            name="Light",
            icon="mdi:lightbulb",
        ),
    ),
}

SWITCHES["WD"] = unique_entities(SWITCHES["WM"], SWITCHES["TD"])


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    entities = []
    for device in hass.data[DOMAIN][entry.unique_id]["hon"].appliances:
        for description in SWITCHES.get(device.appliance_type, []):
            if isinstance(description, HonControlSwitchEntityDescription):
                if description.turn_on_key in device.commands:
                    entities.append(HonControlSwitchEntity(hass, entry, device, description))
            elif isinstance(description, HonConfigSwitchEntityDescription):
                if description.key in device.settings:
                    entities.append(HonConfigSwitchEntity(hass, entry, device, description))
            elif isinstance(description, HonDeviceAttributeSwitchEntityDescription):
                # Check if the attribute exists directly or as a 'Status' value
                if device.get(description.key) is not None or device.get(f"{description.key}Status") is not None:
                    entities.append(HonDeviceAttributeSwitchEntity(hass, entry, device, description))
            elif isinstance(description, HonSwitchEntityDescription):
                if device.get(description.key) is not None:
                    entities.append(HonSwitchEntity(hass, entry, device, description))
    async_add_entities(entities)


class HonSwitchEntity(HonEntity, SwitchEntity):
    entity_description: HonSwitchEntityDescription

    @property
    def is_on(self) -> bool | None:
        """Return True if entity is on."""
        return str(self._device.get(self.entity_description.key, "0")) == "1"

    async def async_turn_on(self, **kwargs: Any) -> None:
        await self._device.set(self.entity_description.key, "1")
        self.coordinator.async_set_updated_data({})
        self.async_write_ha_state()

    async def async_turn_off(self, **kwargs: Any) -> None:
        await self._device.set(self.entity_description.key, "0")
        self.coordinator.async_set_updated_data({})
        self.async_write_ha_state()

    @callback
    def _handle_coordinator_update(self, update: bool = True) -> None:
        self._attr_is_on = self.is_on
        if update:
            self.schedule_update_ha_state()


class HonControlSwitchEntity(HonEntity, SwitchEntity):
    entity_description: HonControlSwitchEntityDescription

    @property
    def is_on(self) -> bool | None:
        """Return True if entity is on."""
        if self.entity_description.key == "delayStatus":
            return int(self._device.get("delayTime", 0)) > 0
        return str(self._device.get(self.entity_description.key, "0")) == "1"

    async def async_turn_on(self, **kwargs: Any) -> None:
        if self.entity_description.turn_on_key in self._device.commands:
            await self._device.commands[self.entity_description.turn_on_key].send()
        self.coordinator.async_set_updated_data({})
        self.async_write_ha_state()

    async def async_turn_off(self, **kwargs: Any) -> None:
        if self.entity_description.turn_off_key in self._device.commands:
            await self._device.commands[self.entity_description.turn_off_key].send()
        self.coordinator.async_set_updated_data({})
        self.async_write_ha_state()
        
    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return the state attributes."""
        result = {}
        if (
            self.entity_description.key == "delayStatus"
            and (delay_time := int(self._device.get("delayTime", 0))) > 0
        ):
            remaining_time = int(self._device.get("remainingTimeMM", 0))
            result["start_time"] = datetime.now() + timedelta(minutes=delay_time)
            result["end_time"] = datetime.now() + timedelta(
                minutes=delay_time + remaining_time
            )
        return result

    @callback
    def _handle_coordinator_update(self, update: bool = True) -> None:
        self._attr_is_on = self.is_on
        if update:
            self.schedule_update_ha_state()


class HonConfigSwitchEntity(HonEntity, SwitchEntity):
    entity_description: HonConfigSwitchEntityDescription

    @property
    def is_on(self) -> bool | None:
        """Return True if entity is on."""
        setting = self._device.settings[self.entity_description.key]
        return (
            setting.value != setting.min
            if hasattr(setting, "min")
            else setting.value == "1"
        )

    async def async_turn_on(self, **kwargs: Any) -> None:
        setting = self._device.settings[self.entity_description.key]
        if type(setting) == HonParameter:
            return
        setting.value = setting.max if isinstance(setting, HonParameterRange) else "1"
        self.coordinator.async_set_updated_data({})
        self.async_write_ha_state()

    async def async_turn_off(self, **kwargs: Any) -> None:
        setting = self._device.settings[self.entity_description.key]
        if type(setting) == HonParameter:
            return
        setting.value = setting.min if isinstance(setting, HonParameterRange) else "0"
        self.coordinator.async_set_updated_data({})
        self.async_write_ha_state()

    @callback
    def _handle_coordinator_update(self, update: bool = True) -> None:
        self._attr_is_on = self.is_on
        if update:
            self.schedule_update_ha_state()


class HonDeviceAttributeSwitchEntity(HonEntity, SwitchEntity):
    """Attribute-based hOn switch entity for changing device settings directly."""

    entity_description: HonDeviceAttributeSwitchEntityDescription

    @property
    def is_on(self) -> bool | None:
        """Return True if entity is on, supporting 'Status' suffix fallback."""
        val = self._device.get(self.entity_description.key)
        if val is None:
            val = self._device.get(f"{self.entity_description.key}Status")
            
        if val is None:
            return False
        return str(val).lower() == str(self.entity_description.turn_on_value).lower()

    async def async_turn_on(self, **kwargs: Any) -> None:
        if self.entity_description.key == "onOffStatus":
            if "startProgram" in self._device.commands:
                if "startProgram.program" in self._device.settings:
                    current_prog = self._device.settings["startProgram.program"].value
                    programs = self._device.settings["startProgram.program"].values
                    
                    # Ensure a valid program is selected before sending the start command
                    if not current_prog or current_prog not in programs:
                        if "auto" in programs:
                            self._device.settings["startProgram.program"].value = "auto"
                        elif "iot_simple_start" in programs:
                            self._device.settings["startProgram.program"].value = "iot_simple_start"
                
                # Optimistically update internal state
                if "onOffStatus" in self._device.settings:
                    self._device.settings["onOffStatus"].value = "1"
                    
                await self._device.commands["startProgram"].send()
        else:
            if self.entity_description.key in self._device.settings:
                self._device.settings[self.entity_description.key].value = self.entity_description.turn_on_value
                if "settings" in self._device.commands:
                    await self._device.commands["settings"].send()
                    
        self.coordinator.async_set_updated_data({})
        self.async_write_ha_state()

    async def async_turn_off(self, **kwargs: Any) -> None:
        if self.entity_description.key == "onOffStatus":
            # Safely turn off using the explicit stop command
            if "stopProgram" in self._device.commands:
                await self._device.commands["stopProgram"].send()
        else:
            if self.entity_description.key in self._device.settings:
                self._device.settings[self.entity_description.key].value = self.entity_description.turn_off_value
                if "settings" in self._device.commands:
                    await self._device.commands["settings"].send()
                    
        self.coordinator.async_set_updated_data({})
        self.async_write_ha_state()

    @callback
    def _handle_coordinator_update(self, update: bool = True) -> None:
        self._attr_is_on = self.is_on
        if update:
            self.schedule_update_ha_state()