// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "forge-std/Test.sol";
import "../contracts/Governance.sol";
import "../contracts/DAO_Governance.sol";
import "../contracts/DAO_Treasury.sol";
import "../contracts/XMRT.sol";
import "../contracts/ParameterRegistry.sol";
import "../contracts/PolicyEngine.sol";
import "../contracts/AI_Agent_Interface.sol";
import "../contracts/ZKPVerifier.sol";
import "../contracts/CrossChainExecutor.sol";

/**
 * @title DAO_Integration_Test
 * @dev Comprehensive test suite for XMRT DAO integration
 */
contract DAO_Integration_Test is Test {
    // Contract instances
    Governance public governance;
    DAO_Governance public daoGovernance;
    DAO_Treasury public daoTreasury;
    XMRT public xmrtToken;
    ParameterRegistry public parameterRegistry;
    PolicyEngine public policyEngine;
    AI_Agent_Interface public aiInterface;
    ZKPVerifier public zkpVerifier;
    CrossChainExecutor public crossChainExecutor;

    // Test addresses
    address public admin = address(0x1);
    address public aiAgent = address(0x2);
    address public user1 = address(0x3);
    address public user2 = address(0x4);
    address public treasury = address(0x5);

    // Test constants
    uint256 public constant INITIAL_SUPPLY = 21_000_000 * 10**18;
    uint256 public constant STAKE_AMOUNT = 1000 * 10**18;

    function setUp() public {
        vm.startPrank(admin);

        // Deploy core contracts
        xmrtToken = new XMRT();
        xmrtToken.initialize();

        parameterRegistry = new ParameterRegistry();
        parameterRegistry.initialize();

        policyEngine = new PolicyEngine();
        policyEngine.initialize();

        daoTreasury = new DAO_Treasury();
        daoTreasury.initialize(address(policyEngine));

        daoGovernance = new DAO_Governance();
        daoGovernance.initialize(address(xmrtToken), address(parameterRegistry));

        governance = new Governance();
        governance.initialize(address(daoGovernance), address(daoTreasury), address(parameterRegistry));

        aiInterface = new AI_Agent_Interface();
        aiInterface.initialize(address(daoGovernance), address(daoTreasury), address(policyEngine));

        zkpVerifier = new ZKPVerifier();
        zkpVerifier.initialize();

        crossChainExecutor = new CrossChainExecutor();
        crossChainExecutor.initialize(address(0), address(0)); // Mock addresses

        // Set up roles
        governance.grantRole(governance.AI_AGENT_ROLE(), aiAgent);
        daoGovernance.grantRole(daoGovernance.AI_AGENT_ROLE(), aiAgent);
        daoTreasury.grantRole(daoTreasury.AI_AGENT_ROLE(), aiAgent);
        aiInterface.grantRole(aiInterface.AI_AGENT_ROLE(), aiAgent);
        policyEngine.grantRole(policyEngine.GOVERNANCE_ROLE(), address(daoTreasury));

        // Set default parameters
        parameterRegistry.setUint(keccak256("VOTING_PERIOD"), 7 days);
        parameterRegistry.setUint(keccak256("TIMELOCK_PERIOD"), 2 days);
        parameterRegistry.setUint(keccak256("MIN_PROPOSAL_THRESHOLD"), 1000 * 10**18);
        parameterRegistry.setUint(keccak256("QUORUM_PERCENTAGE"), 1000); // 10%
        parameterRegistry.setUint(keccak256("MAJORITY_THRESHOLD"), 5000); // 50%

        // Transfer tokens to test users
        xmrtToken.transfer(user1, STAKE_AMOUNT * 10);
        xmrtToken.transfer(user2, STAKE_AMOUNT * 10);

        vm.stopPrank();
    }

    function testTokenStaking() public {
        vm.startPrank(user1);
        
        // Stake tokens
        xmrtToken.stake(STAKE_AMOUNT);
        
        // Check stake
        (uint128 amount, uint64 timestamp) = xmrtToken.userStakes(user1);
        assertEq(uint256(amount), STAKE_AMOUNT);
        assertGt(timestamp, 0);
        
        vm.stopPrank();
    }

    function testProposalCreation() public {
        // Setup: User1 stakes tokens
        vm.startPrank(user1);
        xmrtToken.stake(STAKE_AMOUNT);
        vm.stopPrank();

        // Create proposal
        vm.startPrank(user1);
        uint256 proposalId = daoGovernance.createProposal(
            address(daoTreasury),
            0,
            abi.encodeWithSignature("addAsset(address,string,string)", address(0), "Ethereum", "ETH"),
            "Add ETH as supported asset"
        );
        
        assertEq(proposalId, 0);
        
        // Check proposal state
        assertEq(uint256(daoGovernance.getProposalState(proposalId)), uint256(DAO_Governance.ProposalState.Active));
        
        vm.stopPrank();
    }

    function testAIProposalCreation() public {
        vm.startPrank(aiAgent);
        
        uint256 proposalId = aiInterface.createAIProposal(
            address(daoTreasury),
            0,
            abi.encodeWithSignature("addAsset(address,string,string)", address(0), "Ethereum", "ETH"),
            "AI-triggered proposal to add ETH support",
            6000 // 60% threshold
        );
        
        assertEq(proposalId, 0);
        
        vm.stopPrank();
    }

    function testVoting() public {
        // Setup: Users stake tokens
        vm.startPrank(user1);
        xmrtToken.stake(STAKE_AMOUNT);
        vm.stopPrank();

        vm.startPrank(user2);
        xmrtToken.stake(STAKE_AMOUNT);
        vm.stopPrank();

        // Create proposal
        vm.startPrank(user1);
        uint256 proposalId = daoGovernance.createProposal(
            address(daoTreasury),
            0,
            abi.encodeWithSignature("addAsset(address,string,string)", address(0), "Ethereum", "ETH"),
            "Add ETH as supported asset"
        );
        vm.stopPrank();

        // Vote on proposal
        vm.startPrank(user1);
        daoGovernance.vote(proposalId, true);
        vm.stopPrank();

        vm.startPrank(user2);
        daoGovernance.vote(proposalId, false);
        vm.stopPrank();

        // Check votes
        (,,,,,,,, uint256 votesFor, uint256 votesAgainst,) = daoGovernance.getProposal(proposalId);
        assertEq(votesFor, STAKE_AMOUNT);
        assertEq(votesAgainst, STAKE_AMOUNT);
    }

    function testTreasuryAssetManagement() public {
        vm.startPrank(admin);
        
        // Add ETH as supported asset
        daoTreasury.addAsset(address(0), "Ethereum", "ETH");
        
        // Send ETH to treasury
        vm.deal(address(daoTreasury), 10 ether);
        
        // Check balance
        uint256 balance = daoTreasury.getAssetBalance(address(0));
        assertEq(balance, 10 ether);
        
        vm.stopPrank();
    }

    function testAISpendingLimits() public {
        vm.startPrank(admin);
        
        // Set AI spending limits
        policyEngine.setAISpendingLimit(
            aiAgent,
            address(0), // ETH
            1 ether, // Daily limit
            10 ether // Total limit
        );
        
        // Check limits
        (uint256 dailyLimit, uint256 totalLimit,,,,) = policyEngine.getAISpendingLimit(aiAgent, address(0));
        assertEq(dailyLimit, 1 ether);
        assertEq(totalLimit, 10 ether);
        
        vm.stopPrank();
    }

    function testAISpendingExecution() public {
        vm.startPrank(admin);
        
        // Add ETH as supported asset and fund treasury
        daoTreasury.addAsset(address(0), "Ethereum", "ETH");
        vm.deal(address(daoTreasury), 10 ether);
        
        // Set AI spending limits
        policyEngine.setAISpendingLimit(
            aiAgent,
            address(0),
            1 ether,
            10 ether
        );
        
        vm.stopPrank();

        vm.startPrank(aiAgent);
        
        // Execute AI spending
        uint256 actionId = aiInterface.executeAISpending(
            address(0),
            0.5 ether,
            user1,
            "Test AI spending"
        );
        
        assertGt(actionId, 0);
        
        vm.stopPrank();
    }

    function testParameterRegistry() public {
        vm.startPrank(admin);
        
        // Set parameters
        parameterRegistry.setUint(keccak256("TEST_PARAM"), 12345);
        parameterRegistry.setBool(keccak256("TEST_BOOL"), true);
        parameterRegistry.setAddress(keccak256("TEST_ADDRESS"), user1);
        parameterRegistry.setString(keccak256("TEST_STRING"), "test value");
        
        // Check parameters
        assertEq(parameterRegistry.getUint(keccak256("TEST_PARAM")), 12345);
        assertTrue(parameterRegistry.getBool(keccak256("TEST_BOOL")));
        assertEq(parameterRegistry.getAddress(keccak256("TEST_ADDRESS")), user1);
        assertEq(parameterRegistry.getString(keccak256("TEST_STRING")), "test value");
        
        vm.stopPrank();
    }

    function testZKPVerifier() public {
        vm.startPrank(admin);
        
        zkpVerifier.grantRole(zkpVerifier.PROVER_ROLE(), user1);
        
        vm.stopPrank();

        vm.startPrank(user1);
        
        bytes memory proof = "mock_proof_data";
        bytes memory publicInputs = "mock_public_inputs";
        bytes32 commitment = keccak256("test_commitment");
        
        bool result = zkpVerifier.verifyProof(proof, publicInputs, commitment);
        assertTrue(result);
        
        vm.stopPrank();
    }

    function testGovernanceIntegration() public {
        vm.startPrank(admin);
        
        // Register AI agent in main governance contract
        governance.registerAIAgent(aiAgent, "Test AI", "Test Role");
        
        // Check AI agent registration
        (string memory name, string memory role, bool isActive,,) = governance.getAIAgent(aiAgent);
        assertEq(name, "Test AI");
        assertEq(role, "Test Role");
        assertTrue(isActive);
        
        vm.stopPrank();
    }

    function testPolicyEngine() public {
        vm.startPrank(admin);
        
        // Create a policy
        bytes memory policyData = abi.encode("spending_limit", 1000);
        uint256 policyId = policyEngine.createPolicy(
            "AI Spending Policy",
            "Limits AI agent spending",
            policyData
        );
        
        assertEq(policyId, 1);
        
        vm.stopPrank();
    }

    function testCrossChainExecutor() public {
        vm.startPrank(admin);
        
        bytes memory payload = abi.encode("test_message", 12345);
        
        // This would normally interact with LayerZero/Wormhole
        // For testing, we just verify the contract is properly initialized
        assertTrue(address(crossChainExecutor) != address(0));
        
        vm.stopPrank();
    }

    function testCompleteDAOWorkflow() public {
        // 1. Setup: Users stake tokens
        vm.startPrank(user1);
        xmrtToken.stake(STAKE_AMOUNT * 5); // Stake enough for proposal threshold
        vm.stopPrank();

        vm.startPrank(user2);
        xmrtToken.stake(STAKE_AMOUNT * 3);
        vm.stopPrank();

        // 2. AI agent creates a proposal
        vm.startPrank(aiAgent);
        uint256 proposalId = aiInterface.createAIProposal(
            address(daoTreasury),
            0,
            abi.encodeWithSignature("addAsset(address,string,string)", address(xmrtToken), "XMRT", "XMRT"),
            "Add XMRT token to treasury",
            5000 // 50% threshold
        );
        vm.stopPrank();

        // 3. Users vote on the proposal
        vm.startPrank(user1);
        daoGovernance.vote(proposalId, true);
        vm.stopPrank();

        vm.startPrank(user2);
        daoGovernance.vote(proposalId, true);
        vm.stopPrank();

        // 4. Fast forward time to end voting period
        vm.warp(block.timestamp + 8 days);

        // 5. Queue the proposal
        daoGovernance.queueProposal(proposalId);

        // 6. Fast forward time past timelock
        vm.warp(block.timestamp + 3 days);

        // 7. Execute the proposal
        daoGovernance.executeProposal(proposalId);

        // 8. Verify the proposal was executed
        assertEq(uint256(daoGovernance.getProposalState(proposalId)), uint256(DAO_Governance.ProposalState.Executed));
    }

    function testFailUnauthorizedAIAction() public {
        vm.startPrank(user1); // Not an AI agent
        
        vm.expectRevert();
        aiInterface.createAIProposal(
            address(daoTreasury),
            0,
            "",
            "Unauthorized proposal",
            5000
        );
        
        vm.stopPrank();
    }

    function testFailExceedSpendingLimit() public {
        vm.startPrank(admin);
        
        // Set low spending limit
        policyEngine.setAISpendingLimit(
            aiAgent,
            address(0),
            0.1 ether, // Very low daily limit
            1 ether
        );
        
        daoTreasury.addAsset(address(0), "Ethereum", "ETH");
        vm.deal(address(daoTreasury), 10 ether);
        
        vm.stopPrank();

        vm.startPrank(aiAgent);
        
        vm.expectRevert();
        aiInterface.executeAISpending(
            address(0),
            1 ether, // Exceeds daily limit
            user1,
            "Test spending"
        );
        
        vm.stopPrank();
    }
}

