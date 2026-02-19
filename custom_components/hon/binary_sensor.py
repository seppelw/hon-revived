import logging
from dataclasses import dataclass

from homeassistant.components.binary_sensor import (
    BinarySensorEntityDescription,
    BinarySensorDeviceClass,
    BinarySensorEntity,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import callback
from homeassistant.helpers.entity import EntityCategory
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.core import HomeAssistant

from .const import DOMAIN
from .entity import HonEntity
from .util import unique_entities

_LOGGER = logging.getLogger(__name__)


@dataclass(frozen=True)
class HonBinarySensorEntityDescription(BinarySensorEntityDescription):
    on_value: str | float = ""
    # Erweiterung für mehrere mögliche ON-Werte (z.B. für workingMode)
    on_values: tuple[str, ...] = ()


BINARY_SENSORS: dict[str, tuple[HonBinarySensorEntityDescription, ...]] = {
    "WM": (
        HonBinarySensorEntityDescription(
            key="attributes.lastConnEvent.category",
            name="Remote Control",
            device_class=BinarySensorDeviceClass.CONNECTIVITY,
            on_value="CONNECTED",
            icon="mdi:remote",
            translation_key="remote_control",
        ),
        HonBinarySensorEntityDescription(
            key="doorLockStatus",
            name="Door Lock",
            device_class=BinarySensorDeviceClass.LOCK,
            on_value=0,
            translation_key="door_lock",
        ),
        HonBinarySensorEntityDescription(
            key="doorStatus",
            name="Door",
            device_class=BinarySensorDeviceClass.DOOR,
            on_value=1,
            translation_key="door_open",
        ),
    ),
    "TD": (
        HonBinarySensorEntityDescription(
            key="attributes.lastConnEvent.category",
            name="Remote Control",
            device_class=BinarySensorDeviceClass.CONNECTIVITY,
            on_value="CONNECTED",
            icon="mdi:remote",
            translation_key="remote_control",
        ),
        HonBinarySensorEntityDescription(
            key="doorStatus",
            name="Door",
            device_class=BinarySensorDeviceClass.DOOR,
            on_value=1,
            translation_key="door_open",
        ),
        HonBinarySensorEntityDescription(
            key="doorLockStatus",
            name="Door Lock",
            device_class=BinarySensorDeviceClass.LOCK,
            on_value=0,
            translation_key="door_lock",
        ),
    ),
    "OV": (
        HonBinarySensorEntityDescription(
            key="attributes.lastConnEvent.category",
            name="Remote Control",
            device_class=BinarySensorDeviceClass.CONNECTIVITY,
            on_value="CONNECTED",
            icon="mdi:remote",
            translation_key="remote_control",
        ),
        HonBinarySensorEntityDescription(
            key="doorStatus",
            name="Door",
            device_class=BinarySensorDeviceClass.DOOR,
            on_value=1,
            translation_key="door_open",
        ),
        HonBinarySensorEntityDescription(
            key="doorLockStatus",
            name="Door Lock",
            device_class=BinarySensorDeviceClass.LOCK,
            on_value=0,
            translation_key="door_lock",
        ),
        HonBinarySensorEntityDescription(
            key="remoteCtrValid",
            name="Remote Control",
            device_class=BinarySensorDeviceClass.CONNECTIVITY,
            on_value=1,
            icon="mdi:remote",
            translation_key="remote_control",
        ),
        HonBinarySensorEntityDescription(
            key="preheatStatus",
            name="Preheat",
            icon="mdi:thermometer-chevron-up",
            on_value=1,
            translation_key="preheat",
        ),
    ),
    "IH": (
        HonBinarySensorEntityDescription(
            key="attributes.lastConnEvent.category",
            name="Remote Control",
            device_class=BinarySensorDeviceClass.CONNECTIVITY,
            on_value="CONNECTED",
            icon="mdi:remote",
            translation_key="remote_control",
        ),
    ),
    "DW": (
        HonBinarySensorEntityDescription(
            key="attributes.lastConnEvent.category",
            name="Remote Control",
            device_class=BinarySensorDeviceClass.CONNECTIVITY,
            on_value="CONNECTED",
            icon="mdi:remote",
            translation_key="remote_control",
        ),
        HonBinarySensorEntityDescription(
            key="doorStatus",
            name="Door",
            device_class=BinarySensorDeviceClass.DOOR,
            on_value=1,
            translation_key="door_open",
        ),
    ),
    "AC": (
        HonBinarySensorEntityDescription(
            key="attributes.lastConnEvent.category",
            name="Remote Control",
            device_class=BinarySensorDeviceClass.CONNECTIVITY,
            on_value="CONNECTED",
            icon="mdi:remote",
            translation_key="remote_control",
        ),
    ),
    "REF": (
        HonBinarySensorEntityDescription(
            key="attributes.lastConnEvent.category",
            name="Remote Control",
            device_class=BinarySensorDeviceClass.CONNECTIVITY,
            on_value="CONNECTED",
            icon="mdi:remote",
            translation_key="remote_control",
        ),
        HonBinarySensorEntityDescription(
            key="doorStatusZ1",
            name="Door Status Fridge",
            icon="mdi:fridge",
            device_class=BinarySensorDeviceClass.DOOR,
            on_value=1,
            translation_key="door_open",
        ),
        HonBinarySensorEntityDescription(
            key="doorStatusZ2",
            name="Door Status Freezer",
            icon="mdi:fridge",
            device_class=BinarySensorDeviceClass.DOOR,
            on_value=1,
            translation_key="door_open",
        ),
    ),
    "HO": (
        HonBinarySensorEntityDescription(
            key="attributes.lastConnEvent.category",
            name="Remote Control",
            device_class=BinarySensorDeviceClass.CONNECTIVITY,
            on_value="CONNECTED",
            icon="mdi:remote",
            translation_key="remote_control",
        ),
    ),
    "WC": (
        HonBinarySensorEntityDescription(
            key="attributes.lastConnEvent.category",
            name="Remote Control",
            device_class=BinarySensorDeviceClass.CONNECTIVITY,
            on_value="CONNECTED",
            icon="mdi:remote",
            translation_key="remote_control",
        ),
    ),
    "AP": (
        HonBinarySensorEntityDescription(
            key="attributes.lastConnEvent.category",
            name="Remote Control",
            device_class=BinarySensorDeviceClass.CONNECTIVITY,
            on_value="CONNECTED",
            icon="mdi:remote",
            translation_key="remote_control",
        ),
    ),
    "FRE": (
        HonBinarySensorEntityDescription(
            key="attributes.lastConnEvent.category",
            name="Remote Control",
            device_class=BinarySensorDeviceClass.CONNECTIVITY,
            on_value="CONNECTED",
            icon="mdi:remote",
            translation_key="remote_control",
        ),
        HonBinarySensorEntityDescription(
            key="doorStatus",
            name="Door Status",
            icon="mdi:fridge",
            device_class=BinarySensorDeviceClass.DOOR,
            on_value=1,
            translation_key="door_open",
        ),
    ),
    # --- HEAT PUMP (AW) SECTION ---
    "AW": (
        HonBinarySensorEntityDescription(
            key="onOffStatus",
            name="Power Status",
            device_class=BinarySensorDeviceClass.POWER,
            on_value="1",
            translation_key="power_status",
        ),
        HonBinarySensorEntityDescription(
            key="heatingStatus",
            name="Heating Mode",
            icon="mdi:radiator",
            on_values=("1", "2"),  # 1=Heat, 2=DHW+Heat (aus workingMode)
            device_class=BinarySensorDeviceClass.RUNNING,
            translation_key="heating_mode",
        ),
        HonBinarySensorEntityDescription(
            key="dhwStatus",
            name="DHW Mode",
            icon="mdi:water-boiler",
            on_values=("2", "3"),  # 3=DHW, 2=DHW+Heat (aus workingMode)
            device_class=BinarySensorDeviceClass.RUNNING,
            translation_key="dhw_mode",
        ),
        HonBinarySensorEntityDescription(
            key="quietModeStatus",
            name="Quiet Mode",
            icon="mdi:volume-mute",
            device_class=BinarySensorDeviceClass.RUNNING,
            on_value="1",
            translation_key="quiet_mode",
        ),
        HonBinarySensorEntityDescription(
            key="ecoModeStatus",
            name="Eco Mode",
            icon="mdi:leaf",
            device_class=BinarySensorDeviceClass.RUNNING,
            on_value="1",
            translation_key="eco_mode",
        ),
        HonBinarySensorEntityDescription(
            key="dhwPriorityStatus",
            name="DHW Priority",
            icon="mdi:water-plus",
            entity_category=EntityCategory.DIAGNOSTIC,
            on_value="1",
            translation_key="dhw_priority",
        ),
        HonBinarySensorEntityDescription(
            key="boilerActState",
            name="Boiler Status",
            icon="mdi:heating-coil",
            device_class=BinarySensorDeviceClass.HEAT,
            on_value="1",
            translation_key="boiler_status",
        ),
        HonBinarySensorEntityDescription(
            key="iduElectricHeaterActState1",
            name="Heater 1 Status",
            icon="mdi:heating-coil",
            device_class=BinarySensorDeviceClass.HEAT,
            entity_category=EntityCategory.DIAGNOSTIC,
            on_value="1",
            translation_key="heater1_status",
        ),
        HonBinarySensorEntityDescription(
            key="iduElectricHeaterActState2",
            name="Heater 2 Status",
            icon="mdi:heating-coil",
            device_class=BinarySensorDeviceClass.HEAT,
            entity_category=EntityCategory.DIAGNOSTIC,
            on_value="1",
            translation_key="heater2_status",
        ),
        HonBinarySensorEntityDescription(
            key="holidayActState",
            name="Holiday Mode",
            icon="mdi:island",
            on_value="1",
            translation_key="holiday_mode",
        ),
        HonBinarySensorEntityDescription(
            key="sterilizationModeStatus",
            name="Sterilization",
            icon="mdi:shield-check",
            device_class=BinarySensorDeviceClass.HEAT,
            on_value="1",
            translation_key="sterilization",
        ),
        HonBinarySensorEntityDescription(
            key="attributes.lastConnEvent.category",
            name="Remote Control",
            device_class=BinarySensorDeviceClass.CONNECTIVITY,
            on_value="CONNECTED",
            icon="mdi:remote",
            translation_key="remote_control",
        ),
    ),
}

BINARY_SENSORS["WD"] = unique_entities(BINARY_SENSORS["WM"], BINARY_SENSORS["TD"])


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    entities = []
    for device in hass.data[DOMAIN][entry.unique_id]["hon"].appliances:
        for description in BINARY_SENSORS.get(device.appliance_type, []):
            # Check if key exists or if it is a special mode sensor
            if (device.get(description.key) is not None) or \
               (description.key in ["heatingStatus", "dhwStatus"] and device.get("workingMode") is not None):
                
                if description.key in ["heatingStatus", "dhwStatus"]:
                    entities.append(HonBinaryModeSensorEntity(hass, entry, device, description))
                else:
                    entities.append(HonBinarySensorEntity(hass, entry, device, description))
                    
    async_add_entities(entities)


class HonBinarySensorEntity(HonEntity, BinarySensorEntity):
    entity_description: HonBinarySensorEntityDescription

    def __init__(self, hass, entry, device, description) -> None:
        super().__init__(hass, entry, device, description)
        self._attr_unique_id = f"{device.unique_id}_{description.key}"
        self._attr_name = f"{device.nick_name} {description.name}"

    @property
    def is_on(self) -> bool:
        attr = self._device.get(self.entity_description.key, None)
        value = attr.value if hasattr(attr, "value") else attr
        
        if value is None:
            return False
            
        # Robust comparison: handle string/int/bool
        str_val = str(value).lower()
        target_val = str(self.entity_description.on_value).lower()
        
        # Standard check
        if str_val == target_val:
            return True
            
        # Fallback for generic boolean values
        if str_val in ["true", "on", "yes", "1"] and target_val in ["1", "true"]:
            return True
            
        return False

    @callback
    def _handle_coordinator_update(self, update: bool = True) -> None:
        attr = self._device.get(self.entity_description.key, None)
        value = attr.value if hasattr(attr, "value") else attr
        
        # Force state update for UI
        if update:
            self.schedule_update_ha_state()


class HonBinaryModeSensorEntity(HonBinarySensorEntity):
    """Spezial-Sensor der auf workingMode reagiert."""
    
    @property
    def is_on(self) -> bool:
        mode = self._device.get("workingMode")
        if mode is None:
            return False
            
        str_mode = str(mode)
        # Check against list of valid 'ON' values (e.g. "1" and "2" for heating)
        return any(str_mode == str(val) for val in self.entity_description.on_values)