// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "@openzeppelin/contracts-upgradeable/access/AccessControlUpgradeable.sol";
import "@openzeppelin/contracts-upgradeable/proxy/utils/Initializable.sol";
import "@openzeppelin/contracts-upgradeable/proxy/utils/UUPSUpgradeable.sol";

/**
 * @title AIAgentRegistry
 * @dev A dedicated contract for comprehensive AI agent management, including registration, role assignment, status tracking, and reputation.
 */
contract AIAgentRegistry is Initializable, AccessControlUpgradeable, UUPSUpgradeable {
    // Roles
    bytes32 public constant ADMIN_ROLE = keccak256("ADMIN_ROLE");
    bytes32 public constant AI_AGENT_ROLE = keccak256("AI_AGENT_ROLE");

    // AI agent configuration
    struct AIAgent {
        address agentAddress;
        string name;
        string role;
        bool isActive;
        uint256 actionsExecuted;
        uint256 lastActionTime;
        uint256 reputationScore; // New: Reputation score for the agent
    }

    mapping(address => AIAgent) public aiAgents;
    address[] public aiAgentList;

    // Events
    event AIAgentRegistered(address indexed agent, string name, string role);
    event AIAgentDeactivated(address indexed agent);
    event AIAgentUpdated(address indexed agent, string name, string role, bool isActive);
    event AIAgentReputationUpdated(address indexed agent, uint256 newReputationScore);

    /// @custom:oz-upgrades-unsafe-allow constructor
    constructor() {
        _disableInitializers();
    }

    function initialize() public initializer {
        __AccessControl_init();
        __UUPSUpgradeable_init();

        _grantRole(DEFAULT_ADMIN_ROLE, msg.sender);
        _grantRole(ADMIN_ROLE, msg.sender);
    }

    /**
     * @dev Register a new AI agent
     * Only callable by ADMIN_ROLE.
     * @param agentAddress The address of the AI agent.
     * @param name The name of the AI agent.
     * @param role The role of the AI agent (e.g., "Governance", "Treasury").
     */
    function registerAIAgent(
        address agentAddress,
        string memory name,
        string memory role
    ) external onlyRole(ADMIN_ROLE) {
        require(agentAddress != address(0), "Invalid agent address");
        require(!aiAgents[agentAddress].isActive, "Agent already registered");

        aiAgents[agentAddress] = AIAgent({
            agentAddress: agentAddress,
            name: name,
            role: role,
            isActive: true,
            actionsExecuted: 0,
            lastActionTime: 0,
            reputationScore: 100 // Initialize with a default reputation score
        });

        aiAgentList.push(agentAddress);
        _grantRole(AI_AGENT_ROLE, agentAddress);

        emit AIAgentRegistered(agentAddress, name, role);
    }

    /**
     * @dev Deactivate an AI agent.
     * Only callable by ADMIN_ROLE.
     * @param agentAddress The address of the AI agent to deactivate.
     */
    function deactivateAIAgent(address agentAddress) external onlyRole(ADMIN_ROLE) {
        require(aiAgents[agentAddress].isActive, "Agent not active");
        
        aiAgents[agentAddress].isActive = false;
        _revokeRole(AI_AGENT_ROLE, agentAddress);

        emit AIAgentDeactivated(agentAddress);
    }

    /**
     * @dev Update an existing AI agent's information.
     * Only callable by ADMIN_ROLE.
     * @param agentAddress The address of the AI agent to update.
     * @param name The new name of the AI agent.
     * @param role The new role of the AI agent.
     * @param isActive The new active status of the AI agent.
     */
    function updateAIAgent(
        address agentAddress,
        string memory name,
        string memory role,
        bool isActive
    ) external onlyRole(ADMIN_ROLE) {
        require(aiAgents[agentAddress].agentAddress != address(0), "Agent not found");

        aiAgents[agentAddress].name = name;
        aiAgents[agentAddress].role = role;
        aiAgents[agentAddress].isActive = isActive;

        if (isActive) {
            _grantRole(AI_AGENT_ROLE, agentAddress);
        } else {
            _revokeRole(AI_AGENT_ROLE, agentAddress);
        }

        emit AIAgentUpdated(agentAddress, name, role, isActive);
    }

    /**
     * @dev Update an AI agent's reputation score.
     * This function could be called by a DAO vote or an oracle.
     * @param agentAddress The address of the AI agent.
     * @param newReputationScore The new reputation score.
     */
    function updateAIAgentReputation(address agentAddress, uint256 newReputationScore) external onlyRole(ADMIN_ROLE) {
        require(aiAgents[agentAddress].agentAddress != address(0), "Agent not found");
        aiAgents[agentAddress].reputationScore = newReputationScore;
        emit AIAgentReputationUpdated(agentAddress, newReputationScore);
    }

    /**
     * @dev Increment the actions executed count for an AI agent.
     * Only callable by AI_AGENT_ROLE.
     * @param agentAddress The address of the AI agent.
     */
    function incrementActionsExecuted(address agentAddress) external onlyRole(AI_AGENT_ROLE) {
        require(aiAgents[agentAddress].isActive, "Agent not active");
        aiAgents[agentAddress].actionsExecuted++;
        aiAgents[agentAddress].lastActionTime = block.timestamp;
    }

    /**
     * @dev Get AI agent information.
     * @param agentAddress The address of the AI agent.
     * @return name The name of the AI agent.
     * @return role The role of the AI agent.
     * @return isActive The active status of the AI agent.
     * @return actionsExecuted The number of actions executed by the AI agent.
     * @return lastActionTime The timestamp of the last action executed by the AI agent.
     * @return reputationScore The reputation score of the AI agent.
     */
    function getAIAgent(address agentAddress) external view returns (
        string memory name,
        string memory role,
        bool isActive,
        uint256 actionsExecuted,
        uint256 lastActionTime,
        uint256 reputationScore
    ) {
        AIAgent storage agent = aiAgents[agentAddress];
        return (
            agent.name,
            agent.role,
            agent.isActive,
            agent.actionsExecuted,
            agent.lastActionTime,
            agent.reputationScore
        );
    }

    /**
     * @dev Get all registered AI agents.
     * @return An array of all registered AI agent addresses.
     */
    function getAllAIAgents() external view returns (address[] memory) {
        return aiAgentList;
    }

    /**
     * @dev Authorize contract upgrades.
     */
    function _authorizeUpgrade(address newImplementation) internal override onlyRole(ADMIN_ROLE) {}
}


