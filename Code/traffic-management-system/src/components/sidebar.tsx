'use client'
import { MoreVertical, ChevronFirst, ChevronDown, ChevronRight, AlignLeft, MapPin, SlidersHorizontal } from "lucide-react";
import { createContext, useState, useContext, ReactNode } from "react";

interface SidebarContextType {
  expanded: boolean;
  expandedItem: string | null;
  toggleItem: (text: string) => void;
}

const SidebarContext = createContext<SidebarContextType | undefined>(undefined);

export default function Sidebar({ children }: { children: ReactNode }) {
  const [expanded, setExpanded] = useState(true);
  const [expandedItem, setExpandedItem] = useState<string | null>(null);

  const toggleItem = (text: string) => {
    setExpandedItem((curr) => (curr === text ? null : text));
  };

  return (
    <aside className="h-screen transition-width duration-300">
      <nav className="h-full flex flex-col bg-white border-r shadow-sm">
        <div className="p-4 pb-2 flex justify-between items-center">
          <button
            className="p-1.5 rounded-lg bg-gray-50 hover:bg-gray-100"
            onClick={() => setExpanded((curr) => !curr)}
          >
            <ChevronFirst className={`transition-transform duration-200 ${expanded ? 'rotate-180' : ''}`} />
          </button>
        </div>

        <SidebarContext.Provider value={{ expanded, expandedItem, toggleItem }}>
          <ul className="flex-1 px-3">{children}</ul>
        </SidebarContext.Provider>

        <div className="border-t flex p-3">
          <div
            className={`
              flex justify-between items-center
              overflow-hidden transition-all ${expanded ? "w-52 ml-3" : "w-0"}
          `}
          >
            <div className="leading-4">
              <h4 className="font-semibold">Jordan Teye</h4>
              <span className="text-xs text-gray-600">teyejordan@gmail.com</span>
            </div>
            <MoreVertical size={20} />
          </div>
        </div>
      </nav>
    </aside>
  );
}

export function SidebarItem({
  icon,
  text,
  active,
  alert,
  children
}: {
  icon: React.ReactNode;
  text: string;
  active: boolean;
  alert: boolean;
  children?: ReactNode;
}) {
  const context = useContext(SidebarContext);
  const expanded = context?.expanded;
  const expandedItem = context?.expandedItem;
  const toggleItem = context?.toggleItem;

  const isItemExpanded = expandedItem === text;

  return (
    <li
      className={`
        relative flex flex-col py-2 px-3 my-1
        font-medium rounded-md cursor-pointer
        transition-colors group
        ${active ? "bg-gradient-to-tr from-indigo-200 to-indigo-100 text-indigo-800" : "hover:bg-indigo-50 text-gray-600"}
      `}
      onClick={() => toggleItem && toggleItem(text)}
    >
      <div className="flex items-center justify-between">
        <div className="flex items-center">
          {icon}
          <span
            className={`overflow-hidden whitespace-nowrap transition-all duration-300 ${
              expanded ? "w-auto ml-3" : "w-0"
            }`}
            style={{ maxWidth: expanded ? '100%' : '0' }}
          >
            {text}
          </span>
          {alert && (
            <div
              className={`absolute right-2 w-2 h-2 rounded bg-indigo-400 ${
                expanded ? "" : "top-2"
              }`}
            />
          )}
          {!expanded && (
            <div
              className={`
                absolute left-full rounded-md px-2 py-1 ml-6
                bg-indigo-100 text-indigo-800 text-sm
                invisible opacity-20 -translate-x-3 transition-all
                group-hover:visible group-hover:opacity-100 group-hover:translate-x-0
              `}
            >
              {text}
            </div>
          )}
        </div>
        {(text === "Automation Controls" || text === "Traffic Phases") && (
          <div className="ml-2">
            {isItemExpanded ? <ChevronDown size={20} /> : <ChevronRight size={20} />}
          </div>
        )}
      </div>
      {isItemExpanded && text === "Automation Controls" && (
        <div className="mt-2 bg-white border rounded-md shadow-lg flex flex-col">
          <button className="py-2 px-4 hover:bg-gray-100">Optimized</button>
          <button className="py-2 px-4 hover:bg-gray-100">Default</button>
        </div>
      )}
      {isItemExpanded && text === "Traffic Phases" && (
        <div className="mt-2 bg-white border rounded-md shadow-lg flex flex-col h-48 overflow-y-auto">
          {children}
        </div>
      )}
    </li>
  );
}

// Usage example for Traffic Phases
export function TrafficPhases() {
  const phases = [
    "Phase 1: Red",
    "Phase 2: Green",
    "Phase 3: Yellow",
    // Add more phases as needed
  ];

  return (
    <>
      {phases.map((phase, index) => (
        <div key={index} className="py-2 px-4 hover:bg-gray-100">{phase}</div>
      ))}
    </>
  );
}


