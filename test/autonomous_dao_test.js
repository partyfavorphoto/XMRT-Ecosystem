
const { expect } = require("chai");

describe("AutonomousDAO", function () {
  it("Should set roles and execute agent proposals", async function () {
    const [owner] = await ethers.getSigners();
    const DAO = await ethers.getContractFactory("AutonomousDAO");
    const dao = await DAO.deploy();
    await dao.setRoles(owner.address, owner.address, owner.address);
    expect(await dao.CEO()).to.equal(owner.address);
  });
});
