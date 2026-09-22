import React, { useMemo, useCallback } from 'react';
import {
  ReactFlow,
  MiniMap,
  Controls,
  Background,
  useNodesState,
  useEdgesState,
  Node,
  Edge,
  MarkerType,
  Handle,
  Position,
} from '@xyflow/react';
import '@xyflow/react/dist/style.css';
import { ActionModel } from '../types/action';
import { MigrationBadge } from './MigrationBadge';
import {
  Play,
  CheckCircle,
  HelpCircle,
  RefreshCw,
  GitFork,
  Cloud,
  Monitor,
  AlertTriangle,
  FileCode,
} from 'lucide-react';

interface WorkflowGraphProps {
  actions: ActionModel[];
  onSelectAction: (action: ActionModel) => void;
}

// Custom Node Component
const WorkflowStepNode = ({ data }: { data: any }) => {
  const action: ActionModel = data.action;
  const isSelected = data.isSelected;

  const getNodeIcon = () => {
    if (!action) return <Play className="w-3.5 h-3.5 text-emerald-400" />;
    const cmd = action.command.toLowerCase();
    if (cmd === 'if' || cmd === 'condition') return <GitFork className="w-3.5 h-3.5 text-amber-400" />;
    if (cmd === 'loop') return <RefreshCw className="w-3.5 h-3.5 text-purple-400" />;
    if (cmd === 'runtask' || cmd === 'subtask') return <FileCode className="w-3.5 h-3.5 text-indigo-400" />;
    if (action.cloudOrDesktop === 'Power Automate Cloud') return <Cloud className="w-3.5 h-3.5 text-blue-400" />;
    if (action.cloudOrDesktop === 'Power Automate Desktop') return <Monitor className="w-3.5 h-3.5 text-purple-400" />;
    if (action.cloudOrDesktop === 'Manual Review') return <AlertTriangle className="w-3.5 h-3.5 text-rose-400" />;
    return <CheckCircle className="w-3.5 h-3.5 text-blue-400" />;
  };

  const getBorderColor = () => {
    if (isSelected) return 'border-primary-400 ring-2 ring-primary-500/30';
    if (!action) return 'border-emerald-500/40';
    if (action.cloudOrDesktop === 'Power Automate Cloud') return 'border-blue-500/40 hover:border-blue-400';
    if (action.cloudOrDesktop === 'Power Automate Desktop') return 'border-purple-500/40 hover:border-purple-400';
    if (action.cloudOrDesktop === 'Hybrid') return 'border-amber-500/40 hover:border-amber-400';
    return 'border-rose-500/40 hover:border-rose-400';
  };

  if (data.isStart) {
    return (
      <div className="px-4 py-2.5 rounded-xl bg-slate-900 border-2 border-emerald-500 text-slate-100 shadow-lg shadow-emerald-500/10 flex items-center gap-2">
        <Handle type="source" position={Position.Bottom} className="w-2 h-2 !bg-emerald-400" />
        <Play className="w-4 h-4 text-emerald-400 fill-emerald-400" />
        <span className="text-xs font-bold uppercase tracking-wider">Trigger: Flow Start</span>
      </div>
    );
  }

  if (data.isEnd) {
    return (
      <div className="px-4 py-2.5 rounded-xl bg-slate-900 border-2 border-slate-700 text-slate-300 shadow-lg flex items-center gap-2">
        <Handle type="target" position={Position.Top} className="w-2 h-2 !bg-slate-400" />
        <CheckCircle className="w-4 h-4 text-slate-400" />
        <span className="text-xs font-bold uppercase tracking-wider">Flow End</span>
      </div>
    );
  }

  return (
    <div
      onClick={() => data.onSelect(action)}
      className={`w-64 p-3 rounded-xl bg-slate-900 border-2 ${getBorderColor()} shadow-md cursor-pointer transition-all hover:shadow-lg`}
    >
      <Handle type="target" position={Position.Top} className="w-2 h-2 !bg-slate-500" />
      
      {/* Node Header */}
      <div className="flex items-center justify-between pb-1.5 border-b border-slate-800/80">
        <div className="flex items-center gap-1.5">
          {getNodeIcon()}
          <span className="font-mono text-[11px] font-bold text-slate-400">Step {action.step}</span>
        </div>
        <MigrationBadge type="platform" value={action.cloudOrDesktop} />
      </div>

      {/* A360 Command */}
      <div className="mt-2 text-xs font-bold text-slate-100 flex items-center gap-1">
        <span>{action.command}</span>
        {action.operation && (
          <span className="text-[11px] font-normal text-slate-400 font-mono">→ {action.operation}</span>
        )}
      </div>

      {/* Target PA Equivalent */}
      <div className="mt-1 text-[11px] font-medium text-emerald-400 truncate">
        ↳ {action.powerAutomateAction}
      </div>

      {/* Footer Info */}
      <div className="mt-2 pt-1.5 border-t border-slate-800/60 flex items-center justify-between text-[10px] text-slate-400">
        <span className="truncate max-w-[120px]">{action.task}</span>
        <span className="font-mono font-semibold text-slate-300">{Math.round(action.confidence * 100)}% conf</span>
      </div>

      <Handle type="source" position={Position.Bottom} className="w-2 h-2 !bg-slate-500" />
    </div>
  );
};

const nodeTypes = {
  customStep: WorkflowStepNode,
};

export const WorkflowGraph: React.FC<WorkflowGraphProps> = ({ actions, onSelectAction }) => {
  // Build nodes and edges dynamically based on action sequences
  const { initialNodes, initialEdges } = useMemo(() => {
    const nodes: Node[] = [];
    const edges: Edge[] = [];

    // Start Trigger Node
    nodes.push({
      id: 'node-start',
      type: 'customStep',
      position: { x: 300, y: 30 },
      data: { isStart: true },
    });

    let prevNodeId = 'node-start';
    let currentY = 120;
    const sortedActions = [...actions].sort((a, b) => a.step - b.step);

    sortedActions.forEach((act, idx) => {
      const nodeId = `node-step-${act.step}`;
      // Stagger slightly if nested
      const xOffset = act.parentActionId ? 380 : 300;

      nodes.push({
        id: nodeId,
        type: 'customStep',
        position: { x: xOffset, y: currentY },
        data: {
          action: act,
          onSelect: onSelectAction,
        },
      });

      edges.push({
        id: `edge-${prevNodeId}-${nodeId}`,
        source: prevNodeId,
        target: nodeId,
        type: 'smoothstep',
        animated: act.cloudOrDesktop === 'Hybrid',
        markerEnd: { type: MarkerType.ArrowClosed, color: '#64748b' },
        style: { stroke: act.cloudOrDesktop === 'Power Automate Cloud' ? '#3b82f6' : act.cloudOrDesktop === 'Power Automate Desktop' ? '#a855f7' : '#64748b', strokeWidth: 2 },
      });

      prevNodeId = nodeId;
      currentY += 130;
    });

    // End Node
    nodes.push({
      id: 'node-end',
      type: 'customStep',
      position: { x: 300, y: currentY },
      data: { isEnd: true },
    });

    if (prevNodeId !== 'node-start') {
      edges.push({
        id: `edge-${prevNodeId}-node-end`,
        source: prevNodeId,
        target: 'node-end',
        type: 'smoothstep',
        markerEnd: { type: MarkerType.ArrowClosed, color: '#64748b' },
      });
    }

    return { initialNodes: nodes, initialEdges: edges };
  }, [actions, onSelectAction]);

  const [nodes, setNodes, onNodesChange] = useNodesState(initialNodes);
  const [edges, setEdges, onEdgesChange] = useEdgesState(initialEdges);

  // Update when actions change
  React.useEffect(() => {
    setNodes(initialNodes);
    setEdges(initialEdges);
  }, [initialNodes, initialEdges, setNodes, setEdges]);

  return (
    <div className="w-full h-[720px] rounded-2xl bg-slate-950 border border-slate-800 relative overflow-hidden shadow-inner">
      {/* Legend overlay */}
      <div className="absolute top-4 left-4 z-10 p-3 rounded-xl bg-slate-900/90 backdrop-blur border border-slate-800 text-xs space-y-1.5 shadow-md">
        <span className="text-[11px] font-bold text-slate-400 uppercase tracking-wider block mb-1">
          Node Legend
        </span>
        <div className="flex items-center gap-2 text-blue-400">
          <span className="w-2.5 h-2.5 rounded-full bg-blue-400"></span>
          <span>Power Automate Cloud</span>
        </div>
        <div className="flex items-center gap-2 text-purple-400">
          <span className="w-2.5 h-2.5 rounded-full bg-purple-400"></span>
          <span>Power Automate Desktop</span>
        </div>
        <div className="flex items-center gap-2 text-amber-400">
          <span className="w-2.5 h-2.5 rounded-full bg-amber-400"></span>
          <span>Hybrid Transition</span>
        </div>
        <div className="flex items-center gap-2 text-rose-400">
          <span className="w-2.5 h-2.5 rounded-full bg-rose-400"></span>
          <span>Manual Review</span>
        </div>
      </div>

      <ReactFlow
        nodes={nodes}
        edges={edges}
        onNodesChange={onNodesChange}
        onEdgesChange={onEdgesChange}
        nodeTypes={nodeTypes}
        fitView
        attributionPosition="bottom-right"
      >
        <Background color="#1e293b" gap={20} size={1} />
        <Controls className="!bg-slate-900 !border-slate-800 !text-white fill-white" />
        <MiniMap
          nodeColor={(node) => {
            if (node.data?.isStart) return '#10b981';
            if (node.data?.isEnd) return '#64748b';
            const a = node.data?.action as ActionModel;
            if (!a) return '#3b82f6';
            if (a.cloudOrDesktop === 'Power Automate Cloud') return '#3b82f6';
            if (a.cloudOrDesktop === 'Power Automate Desktop') return '#a855f7';
            if (a.cloudOrDesktop === 'Hybrid') return '#f59e0b';
            return '#ef4444';
          }}
          className="!bg-slate-900 !border-slate-800 rounded-xl overflow-hidden"
        />
      </ReactFlow>
    </div>
  );
};
