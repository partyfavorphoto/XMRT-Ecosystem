// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

import "@openzeppelin/contracts/access/AccessControl.sol";
import "@openzeppelin/contracts/security/ReentrancyGuard.sol";
import "@openzeppelin/contracts/utils/Counters.sol";

/**
 * @title AutonomousAgentRegistry
 * @dev Registry for managing autonomous agents with execution authority
 */
contract AutonomousAgentRegistry is AccessControl, ReentrancyGuard {
    using Counters for Counters.Counter;

    bytes32 public constant ADMIN_ROLE = keccak256("ADMIN_ROLE");
    bytes32 public constant AGENT_ROLE = keccak256("AGENT_ROLE");
    bytes32 public constant EXECUTOR_ROLE = keccak256("EXECUTOR_ROLE");

    Counters.Counter private _agentIds;

    struct Agent {
        uint256 id;
        address agentAddress;
        string name;
        string description;
        uint256 reputation;
        uint256 executionCount;
        bool isActive;
        uint256 registrationTime;
        address registeredBy;
        uint256 stakingAmount;
        AgentType agentType;
        uint256[] permissions;
    }

    enum AgentType {
        GOVERNANCE,
        TREASURY,
        PROPOSAL_EXECUTOR,
        ORACLE,
        SECURITY,
        COMMUNITY
    }

    enum Permission {
        EXECUTE_PROPOSALS,
        MANAGE_TREASURY,
        UPDATE_GOVERNANCE,
        ACCESS_ORACLES,
        EMERGENCY_ACTIONS,
        COMMUNITY_MANAGEMENT
    }

    mapping(uint256 => Agent) public agents;
    mapping(address => uint256) public agentAddressToId;
    mapping(address => bool) public authorizedAgents;
    mapping(uint256 => mapping(uint256 => bool)) public agentPermissions;

    uint256 public minimumStaking = 1000 * 10**18; // 1000 XMRT tokens
    uint256 public totalActiveAgents;

    event AgentRegistered(uint256 indexed agentId, address indexed agentAddress, string name, AgentType agentType);
    event AgentActivated(uint256 indexed agentId, address indexed agentAddress);
    event AgentDeactivated(uint256 indexed agentId, address indexed agentAddress);
    event AgentExecuted(uint256 indexed agentId, address indexed target, bytes data, bool success);
    event PermissionGranted(uint256 indexed agentId, Permission permission);
    event PermissionRevoked(uint256 indexed agentId, Permission permission);
    event ReputationUpdated(uint256 indexed agentId, uint256 newReputation);

    modifier onlyActiveAgent(uint256 agentId) {
        require(agents[agentId].isActive, "Agent is not active");
        _;
    }

    modifier onlyAuthorizedAgent() {
        require(authorizedAgents[msg.sender], "Not an authorized agent");
        _;
    }

    constructor() {
        _grantRole(DEFAULT_ADMIN_ROLE, msg.sender);
        _grantRole(ADMIN_ROLE, msg.sender);
    }

    /**
     * @dev Register a new autonomous agent
     */
    function registerAgent(
        address agentAddress,
        string memory name,
        string memory description,
        AgentType agentType,
        uint256[] memory permissions
    ) external payable nonReentrant {
        require(agentAddress != address(0), "Invalid agent address");
        require(agentAddressToId[agentAddress] == 0, "Agent already registered");
        require(msg.value >= minimumStaking, "Insufficient staking amount");

        _agentIds.increment();
        uint256 newAgentId = _agentIds.current();

        agents[newAgentId] = Agent({
            id: newAgentId,
            agentAddress: agentAddress,
            name: name,
            description: description,
            reputation: 100, // Starting reputation
            executionCount: 0,
            isActive: true,
            registrationTime: block.timestamp,
            registeredBy: msg.sender,
            stakingAmount: msg.value,
            agentType: agentType,
            permissions: permissions
        });

        agentAddressToId[agentAddress] = newAgentId;
        authorizedAgents[agentAddress] = true;
        totalActiveAgents++;

        // Grant permissions
        for (uint256 i = 0; i < permissions.length; i++) {
            agentPermissions[newAgentId][permissions[i]] = true;
        }

        // Grant appropriate roles
        _grantRole(AGENT_ROLE, agentAddress);
        if (agentType == AgentType.PROPOSAL_EXECUTOR || agentType == AgentType.TREASURY) {
            _grantRole(EXECUTOR_ROLE, agentAddress);
        }

        emit AgentRegistered(newAgentId, agentAddress, name, agentType);
    }

    /**
     * @dev Execute a function call through an authorized agent
     */
    function executeAsAgent(
        uint256 agentId,
        address target,
        bytes calldata data
    ) external onlyActiveAgent(agentId) onlyAuthorizedAgent nonReentrant returns (bool success, bytes memory returnData) {
        require(agents[agentId].agentAddress == msg.sender, "Not the registered agent");

        agents[agentId].executionCount++;

        (success, returnData) = target.call(data);

        // Update reputation based on execution success
        if (success) {
            agents[agentId].reputation += 1;
        } else {
            if (agents[agentId].reputation > 0) {
                agents[agentId].reputation -= 1;
            }
        }

        emit AgentExecuted(agentId, target, data, success);
        emit ReputationUpdated(agentId, agents[agentId].reputation);
    }

    /**
     * @dev Grant permission to an agent
     */
    function grantPermission(uint256 agentId, Permission permission) external onlyRole(ADMIN_ROLE) {
        require(agents[agentId].id != 0, "Agent does not exist");
        agentPermissions[agentId][uint256(permission)] = true;
        agents[agentId].permissions.push(uint256(permission));

        emit PermissionGranted(agentId, permission);
    }

    /**
     * @dev Revoke permission from an agent
     */
    function revokePermission(uint256 agentId, Permission permission) external onlyRole(ADMIN_ROLE) {
        require(agents[agentId].id != 0, "Agent does not exist");
        agentPermissions[agentId][uint256(permission)] = false;

        // Remove from permissions array
        uint256[] storage permissions = agents[agentId].permissions;
        for (uint256 i = 0; i < permissions.length; i++) {
            if (permissions[i] == uint256(permission)) {
                permissions[i] = permissions[permissions.length - 1];
                permissions.pop();
                break;
            }
        }

        emit PermissionRevoked(agentId, permission);
    }

    /**
     * @dev Deactivate an agent
     */
    function deactivateAgent(uint256 agentId) external onlyRole(ADMIN_ROLE) {
        require(agents[agentId].isActive, "Agent already inactive");

        agents[agentId].isActive = false;
        authorizedAgents[agents[agentId].agentAddress] = false;
        totalActiveAgents--;

        emit AgentDeactivated(agentId, agents[agentId].agentAddress);
    }

    /**
     * @dev Reactivate an agent
     */
    function reactivateAgent(uint256 agentId) external onlyRole(ADMIN_ROLE) {
        require(!agents[agentId].isActive, "Agent already active");
        require(agents[agentId].id != 0, "Agent does not exist");

        agents[agentId].isActive = true;
        authorizedAgents[agents[agentId].agentAddress] = true;
        totalActiveAgents++;

        emit AgentActivated(agentId, agents[agentId].agentAddress);
    }

    /**
     * @dev Check if agent has specific permission
     */
    function hasPermission(uint256 agentId, Permission permission) external view returns (bool) {
        return agentPermissions[agentId][uint256(permission)];
    }

    /**
     * @dev Get agent information
     */
    function getAgent(uint256 agentId) external view returns (Agent memory) {
        return agents[agentId];
    }

    /**
     * @dev Get agent ID by address
     */
    function getAgentIdByAddress(address agentAddress) external view returns (uint256) {
        return agentAddressToId[agentAddress];
    }

    /**
     * @dev Get total number of registered agents
     */
    function getTotalAgents() external view returns (uint256) {
        return _agentIds.current();
    }

    /**
     * @dev Update minimum staking amount
     */
    function updateMinimumStaking(uint256 newAmount) external onlyRole(ADMIN_ROLE) {
        minimumStaking = newAmount;
    }

    /**
     * @dev Emergency function to pause all agent operations
     */
    function emergencyPause() external onlyRole(ADMIN_ROLE) {
        // Implementation for emergency pause
        // This would disable all agent executions
    }

    /**
     * @dev Withdraw staking amount (only for deactivated agents)
     */
    function withdrawStaking(uint256 agentId) external nonReentrant {
        require(agents[agentId].registeredBy == msg.sender, "Not the agent registrar");
        require(!agents[agentId].isActive, "Agent must be deactivated first");
        require(agents[agentId].stakingAmount > 0, "No staking to withdraw");

        uint256 amount = agents[agentId].stakingAmount;
        agents[agentId].stakingAmount = 0;

        payable(msg.sender).transfer(amount);
    }

    /**
     * @dev Batch execute multiple calls through an agent
     */
    function batchExecuteAsAgent(
        uint256 agentId,
        address[] calldata targets,
        bytes[] calldata data
    ) external onlyActiveAgent(agentId) onlyAuthorizedAgent nonReentrant returns (bool[] memory successes, bytes[] memory returnData) {
        require(agents[agentId].agentAddress == msg.sender, "Not the registered agent");
        require(targets.length == data.length, "Arrays length mismatch");

        successes = new bool[](targets.length);
        returnData = new bytes[](targets.length);

        for (uint256 i = 0; i < targets.length; i++) {
            (successes[i], returnData[i]) = targets[i].call(data[i]);
            agents[agentId].executionCount++;

            emit AgentExecuted(agentId, targets[i], data[i], successes[i]);
        }

        // Update reputation based on overall success rate
        uint256 successCount = 0;
        for (uint256 i = 0; i < successes.length; i++) {
            if (successes[i]) successCount++;
        }

        if (successCount > successes.length / 2) {
            agents[agentId].reputation += successes.length;
        } else {
            if (agents[agentId].reputation > successes.length) {
                agents[agentId].reputation -= successes.length;
            } else {
                agents[agentId].reputation = 0;
            }
        }

        emit ReputationUpdated(agentId, agents[agentId].reputation);
    }
}