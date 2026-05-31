import React, { useState, useEffect } from 'react';

/**
 * Sierra A.V.E.N.G.E.R.S Roster Component
 * 
 * Visual roster of all specialized agents.
 * Can be dropped into App.jsx or a new Agents tab/modal.
 * 
 * Props:
 *   - onChatWithDirector: callback when user wants to chat with Director
 *   - onDelegateTask: callback for complex tasks
 */

const AgentsRoster = ({ onChatWithDirector, onDelegateTask }) => {
  const [agents, setAgents] = useState([
    { name: "director", role: "Director Sierra", goal: "Central orchestrator & your personal AI OS", status: "online" },
    { name: "scout", role: "Scout", goal: "Deep research & intelligence", status: "online" },
    { name: "forge", role: "Forge", goal: "Code engineering & Sierra evolution", status: "online" },
    { name: "chronos", role: "Chronos", goal: "Calendar & time intelligence", status: "online" },
    { name: "courier", role: "Courier", goal: "Email & communications", status: "online" },
    { name: "weaver", role: "Weaver", goal: "Memory & knowledge management", status: "online" },
    { name: "echo", role: "Echo", goal: "Voice & persona layer", status: "online" },
    { name: "sentinel", role: "Sentinel", goal: "Security, privacy & safety", status: "online" },
    { name: "operator", role: "Operator", goal: "Daily operations & workflows", status: "online" },
    { name: "maestro", role: "Maestro", goal: "Meetings & collaboration", status: "online" },
    { name: "creator", role: "Creator", goal: "Content & documentation", status: "online" },
    { name: "evolver", role: "Evolver", goal: "Self-improvement & architecture", status: "online" },
    { name: "guardian", role: "Guardian", goal: "Local files & device privacy", status: "online" },
    { name: "analyst", role: "Analyst", goal: "Personal intelligence briefings", status: "online" },
    { name: "toolsmith", role: "Toolsmith", goal: "Tools & integrations", status: "online" },
  ]);

  const [selectedAgent, setSelectedAgent] = useState(null);
  const [taskInput, setTaskInput] = useState("");

  const handleChat = (agent) => {
    if (agent.name === "director" && onChatWithDirector) {
      onChatWithDirector();
    } else {
      alert(`Chatting directly with ${agent.role} coming soon! (Currently routes through Director)`);
    }
  };

  const handleDelegate = () => {
    if (taskInput.trim() && onDelegateTask) {
      onDelegateTask(taskInput);
      setTaskInput("");
    }
  };

  return (
    <div className="agents-roster p-6 bg-gray-900 text-white rounded-2xl">
      <div className="flex items-center justify-between mb-6">
        <div>
          <h2 className="text-3xl font-bold">Sierra A.V.E.N.G.E.R.S</h2>
          <p className="text-gray-400">15 Specialized Agents • Memory • Voice • Safety</p>
        </div>
        <div className="px-4 py-1 bg-green-600 rounded-full text-sm">All Systems Operational</div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 mb-8">
        {agents.map((agent, index) => (
          <div
            key={index}
            onClick={() => setSelectedAgent(agent)}
            className={`p-4 rounded-xl border cursor-pointer transition-all ${selectedAgent?.name === agent.name ? 'border-blue-500 bg-gray-800' : 'border-gray-700 hover:border-gray-500'}`}
          >
            <div className="flex justify-between items-start">
              <div>
                <div className="font-semibold text-lg">{agent.role}</div>
                <div className="text-sm text-gray-400 mt-1 line-clamp-2">{agent.goal}</div>
              </div>
              <div className="text-green-400 text-xs px-2 py-0.5 bg-green-900/50 rounded">{agent.status}</div>
            </div>
          </div>
        ))}
      </div>

      {selectedAgent && (
        <div className="bg-gray-800 p-5 rounded-xl mb-6">
          <h3 className="font-bold mb-2">{selectedAgent.role}</h3>
          <p className="text-gray-300 mb-4">{selectedAgent.goal}</p>
          
          <div className="flex gap-3">
            <button 
              onClick={() => handleChat(selectedAgent)}
              className="px-5 py-2 bg-blue-600 hover:bg-blue-700 rounded-lg text-sm font-medium"
            >
              Chat with {selectedAgent.role}
            </button>
            
            {selectedAgent.name === "director" && (
              <button 
                onClick={() => handleDelegate()}
                className="px-5 py-2 bg-purple-600 hover:bg-purple-700 rounded-lg text-sm font-medium"
              >
                Delegate Complex Task
              </button>
            )}
          </div>
        </div>
      )}

      <div className="bg-gray-800 p-4 rounded-xl">
        <div className="text-sm text-gray-400 mb-2">Delegate a task to the full roster (via Director)</div>
        <div className="flex gap-2">
          <input
            type="text"
            value={taskInput}
            onChange={(e) => setTaskInput(e.target.value)}
            placeholder="e.g. Research latest AI agents and update my calendar + draft a summary"
            className="flex-1 bg-gray-700 border border-gray-600 rounded-lg px-4 py-2 text-sm"
          />
          <button 
            onClick={handleDelegate}
            className="px-6 py-2 bg-purple-600 hover:bg-purple-700 rounded-lg text-sm font-medium"
          >
            Delegate
          </button>
        </div>
      </div>
    </div>
  );
};

export default AgentsRoster;
