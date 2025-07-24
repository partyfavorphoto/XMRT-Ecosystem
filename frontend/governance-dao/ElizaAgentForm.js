
import { useState } from 'react';

export default function ElizaAgentForm({ contract }) {
  const [ceo, setCeo] = useState("");
  const [agent, setAgent] = useState("");
  const [data, setData] = useState("");

  const setRoles = async () => {
    await contract.setRoles(ceo, ceo, ceo);
  };

  const exec = async () => {
    await contract.executeAgentProposal(agent, data);
  };

  return (
    <div>
      <input placeholder="CEO Address" onChange={e => setCeo(e.target.value)} />
      <button onClick={setRoles}>Set Roles</button>
      <br />
      <input placeholder="Agent Addr" onChange={e => setAgent(e.target.value)} />
      <input placeholder="Data (hex)" onChange={e => setData(e.target.value)} />
      <button onClick={exec}>Execute Agent Proposal</button>
    </div>
  );
}
