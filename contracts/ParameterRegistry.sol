// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "@openzeppelin/contracts-upgradeable/access/AccessControlUpgradeable.sol";
import "@openzeppelin/contracts-upgradeable/proxy/utils/Initializable.sol";
import "@openzeppelin/contracts-upgradeable/proxy/utils/UUPSUpgradeable.sol";

/**
 * @title ParameterRegistry
 * @dev Contract for managing governable parameters of the DAO
 */
contract ParameterRegistry is
    Initializable,
    AccessControlUpgradeable,
    UUPSUpgradeable
{
    bytes32 public constant ADMIN_ROLE = keccak256("ADMIN_ROLE");
    bytes32 public constant GOVERNANCE_ROLE = keccak256("GOVERNANCE_ROLE");

    mapping(bytes32 => uint256) private uintParameters;
    mapping(bytes32 => bool) private boolParameters;
    mapping(bytes32 => address) private addressParameters;
    mapping(bytes32 => string) private stringParameters;

    event UintParameterUpdated(bytes32 indexed key, uint256 oldValue, uint256 newValue);
    event BoolParameterUpdated(bytes32 indexed key, bool oldValue, bool newValue);
    event AddressParameterUpdated(bytes32 indexed key, address oldValue, address newValue);
    event StringParameterUpdated(bytes32 indexed key, string oldValue, string newValue);

    /// @custom:oz-upgrades-unsafe-allow constructor
    constructor() {
        _disableInitializers();
    }

    function initialize() public initializer {
        __AccessControl_init();
        __UUPSUpgradeable_init();

        _grantRole(DEFAULT_ADMIN_ROLE, msg.sender);
        _grantRole(ADMIN_ROLE, msg.sender);
        _grantRole(GOVERNANCE_ROLE, msg.sender);
    }

    /**
     * @dev Set a uint256 parameter
     * Only callable by addresses with GOVERNANCE_ROLE
     */
    function setUint(bytes32 key, uint256 value) external onlyRole(GOVERNANCE_ROLE) {
        emit UintParameterUpdated(key, uintParameters[key], value);
        uintParameters[key] = value;
    }

    /**
     * @dev Get a uint256 parameter
     */
    function getUint(bytes32 key) external view returns (uint256) {
        return uintParameters[key];
    }

    /**
     * @dev Set a bool parameter
     * Only callable by addresses with GOVERNANCE_ROLE
     */
    function setBool(bytes32 key, bool value) external onlyRole(GOVERNANCE_ROLE) {
        emit BoolParameterUpdated(key, boolParameters[key], value);
        boolParameters[key] = value;
    }

    /**
     * @dev Get a bool parameter
     */
    function getBool(bytes32 key) external view returns (bool) {
        return boolParameters[key];
    }

    /**
     * @dev Set an address parameter
     * Only callable by addresses with GOVERNANCE_ROLE
     */
    function setAddress(bytes32 key, address value) external onlyRole(GOVERNANCE_ROLE) {
        emit AddressParameterUpdated(key, addressParameters[key], value);
        addressParameters[key] = value;
    }

    /**
     * @dev Get an address parameter
     */
    function getAddress(bytes32 key) external view returns (address) {
        return addressParameters[key];
    }

    /**
     * @dev Set a string parameter
     * Only callable by addresses with GOVERNANCE_ROLE
     */
    function setString(bytes32 key, string memory value) external onlyRole(GOVERNANCE_ROLE) {
        emit StringParameterUpdated(key, stringParameters[key], value);
        stringParameters[key] = value;
    }

    /**
     * @dev Get a string parameter
     */
    function getString(bytes32 key) external view returns (string memory) {
        return stringParameters[key];
    }

    /**
     * @dev Authorize contract upgrades
     */
    function _authorizeUpgrade(address newImplementation) internal override onlyRole(ADMIN_ROLE) {}
}


