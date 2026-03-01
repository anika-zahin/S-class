import React, { useRef, useState } from "react";
import { ReactSketchCanvas } from "react-sketch-canvas";
import axios from "axios";
import { 
  Pen, Eraser, Zap, RotateCcw, RotateCw, Trash2, PlusCircle, RefreshCw, 
  Loader2, Download, BookOpen, FileText, HelpCircle, Circle, Square, Triangle
} from "lucide-react";

const App = () => {
  const canvasRef = useRef(null);
  
  // UI & Canvas State
  const [penColor, setPenColor] = useState("#0f172a");
  const [strokeWidth, setStrokeWidth] = useState(6);
  const [isEraser, setIsEraser] = useState(false);
  const [activeTab, setActiveTab] = useState("Write");
  const [isLoading, setIsLoading] = useState(false);
  
  // Data State
  const [rawTextVault, setRawTextVault] = useState(""); 
  const [syncCount, setSyncCount] = useState(0); 
  const [fullStudyData, setFullStudyData] = useState({ 
    notes: [], 
    cheatsheet: {}, 
    quiz: [] 
  });

  // --- 1. CANVAS ACTIONS ---
  const handleUndo = () => canvasRef.current.undo();
  const handleRedo = () => canvasRef.current.redo();
  const handleClearCanvas = () => canvasRef.current.clearCanvas();

  // --- 2. BACKEND COMMUNICATION ---
  const handleSyncToAI = async () => {
    setIsLoading(true);
    try {
      const imageData = await canvasRef.current.exportImage("png");
      const blob = await (await fetch(imageData)).blob();
      const formData = new FormData();
      formData.append("file", blob, "board.png");

      const response = await axios.post("http://localhost:8000/sync-board", formData);
      if (response.data.raw_text) {
        setRawTextVault(prev => prev + " " + response.data.raw_text);
        setSyncCount(prev => prev + 1);
        canvasRef.current.clearCanvas();
      }
    } catch (error) {
      alert("Sync failed. Ensure backend is running.");
    } finally {
      setIsLoading(false);
    }
  };

  const generateFinalNotes = async (tab) => {
    if (!rawTextVault && syncCount === 0) return alert("Sync some whiteboard content first!");
    
    setIsLoading(true);
    try {
      const response = await axios.post("http://localhost:8000/generate-final-notes", { 
        all_text: rawTextVault 
      });
      
      // Data Normalization
      setFullStudyData({
        notes: Array.isArray(response.data.notes) ? response.data.notes : [],
        cheatsheet: response.data.cheatsheet || {},
        quiz: Array.isArray(response.data.quiz) ? response.data.quiz : []
      });
      setActiveTab(tab);
    } catch (error) {
      alert("AI Generation failed.");
    } finally {
      setIsLoading(false);
    }
  };

  const downloadPDF = async () => {
    try {
      const res = await axios.post("http://localhost:8000/generate-pdf", 
        { studyData: fullStudyData }, 
        { responseType: 'blob' }
      );
      const url = window.URL.createObjectURL(new Blob([res.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', 'StudyGuide.pdf');
      link.click();
    } catch (e) { alert("PDF Error"); }
  };

  // --- 3. RENDERING LOGIC (SAFE) ---
  const renderNotes = () => {
    const notes = fullStudyData.notes || [];
    if (notes.length === 0) return <p className="text-center py-20 text-slate-400 italic">No notes generated yet.</p>;

    return (
      <div className="space-y-10">
        {notes.map((note, k) => (
          <div key={k} className="animate-in slide-in-from-bottom-4 duration-500">
            <h3 className="text-3xl font-black text-slate-800 mb-2 capitalize border-b-2 border-indigo-50 pb-2">
              {note.title || "Topic"}
            </h3>
            <p className="text-xl text-slate-600 leading-relaxed italic mb-4">
              {note.definition || "Definition pending..."}
            </p>
            {note.image_url && (
              <div className="bg-white p-4 rounded-3xl border-2 border-dashed border-indigo-100 flex flex-col items-center">
                <img 
                  src={`https://placehold.co/600x250/6366f1/ffffff?text=${encodeURIComponent(note.image_url)}`} 
                  className="rounded-2xl shadow-sm mb-2"
                  alt="Diagram"
                />
                <span className="text-xs font-bold text-indigo-400 uppercase tracking-widest">Recommended Visual Aid</span>
              </div>
            )}
          </div>
        ))}
      </div>
    );
  };

  const renderCheatSheet = () => {
    const sheet = fullStudyData.cheatsheet || {};
    const entries = Object.entries(sheet);
    if (entries.length === 0) return <p className="text-center py-20 text-slate-400">Sync board to build cheat sheet.</p>;

    return (
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {entries.map(([topic, bullets], k) => (
          <div key={k} className="bg-white p-8 rounded-[2.5rem] border border-slate-100 shadow-sm hover:shadow-md transition-shadow">
            <h4 className="text-xl font-bold text-indigo-600 mb-4 capitalize flex items-center gap-2">
              <div className="w-1.5 h-5 bg-indigo-500 rounded-full" /> {topic}
            </h4>
            <ul className="space-y-3">
              {(Array.isArray(bullets) ? bullets : [bullets]).map((b, i) => (
                <li key={i} className="flex gap-3 text-slate-600 text-lg">
                  <span className="text-indigo-300 font-bold">•</span>
                  {typeof b === 'object' ? JSON.stringify(b) : b}
                </li>
              ))}
            </ul>
          </div>
        ))}
      </div>
    );
  };

  const renderQuiz = () => {
    const quiz = fullStudyData.quiz || [];
    if (quiz.length === 0) return <p className="text-center py-20 text-slate-400 italic">Generate notes to see your quiz.</p>;

    return (
      <div className="max-w-3xl mx-auto space-y-6">
        {quiz.map((q, i) => (
          <div key={i} className="bg-white p-8 rounded-[2rem] border-2 border-indigo-50 shadow-sm">
            <p className="text-xl font-bold text-slate-800 mb-4">Q: {q.question}</p>
            <details className="group cursor-pointer">
              <summary className="text-indigo-500 font-bold list-none flex items-center gap-2">
                <PlusCircle size={20} className="group-open:rotate-45 transition-transform"/>
                Reveal Answer
              </summary>
              <p className="mt-4 p-4 bg-indigo-50 rounded-xl text-indigo-900 border border-indigo-100 font-medium">
                {q.answer}
              </p>
            </details>
          </div>
        ))}
      </div>
    );
  };

  return (
    <div className="min-h-screen bg-[#f8fafc] p-4 md:p-8 font-sans text-slate-900">
      <header className="max-w-6xl mx-auto flex justify-between items-center mb-8">
        <div className="flex items-center gap-3">
          <Zap className="text-indigo-600 fill-indigo-600" size={32} />
          <h1 className="text-3xl font-black tracking-tighter">S-CLASS STUDY</h1>
        </div>
        <div className="flex gap-4 items-center">
          <div className="bg-white px-6 py-3 rounded-2xl border font-bold shadow-sm flex items-center gap-2">
            <span className="w-3 h-3 bg-emerald-500 rounded-full animate-pulse" />
            {syncCount} Synced
          </div>
          <button onClick={() => window.location.reload()} className="p-3 bg-white border rounded-2xl hover:bg-slate-50 transition-colors">
            <RefreshCw size={20} className="text-slate-400" />
          </button>
        </div>
      </header>

      <nav className="max-w-4xl mx-auto flex gap-2 mb-8 bg-white p-2 rounded-[2rem] border shadow-sm">
        {[
          { id: "Write", icon: <Pen size={18}/> },
          { id: "Notes", icon: <BookOpen size={18}/> },
          { id: "Cheat Sheet", icon: <FileText size={18}/> },
          { id: "Quiz", icon: <HelpCircle size={18}/> }
        ].map(tab => (
          <button 
            key={tab.id} 
            onClick={() => tab.id === "Write" ? setActiveTab("Write") : generateFinalNotes(tab.id)} 
            className={`flex-1 flex items-center justify-center gap-2 py-4 rounded-[1.5rem] font-bold transition-all ${activeTab === tab.id ? "bg-indigo-600 text-white shadow-xl shadow-indigo-100" : "text-slate-400 hover:bg-slate-50"}`}
          >
            {tab.icon} {tab.id}
          </button>
        ))}
      </nav>

      <main className="max-w-6xl mx-auto bg-white rounded-[3rem] shadow-2xl border border-white overflow-hidden min-h-[600px] flex flex-col relative">
        {activeTab === "Write" ? (
          <>
            <div className="p-4 bg-slate-50 border-b flex items-center justify-between">
              <div className="flex items-center gap-2 bg-white p-1 rounded-xl border">
                <button onClick={() => setIsEraser(false)} className={`p-3 rounded-lg ${!isEraser ? 'bg-slate-900 text-white' : 'text-slate-400'}`}><Pen size={20}/></button>
                <button onClick={() => setIsEraser(true)} className={`p-3 rounded-lg ${isEraser ? 'bg-slate-900 text-white' : 'text-slate-400'}`}><Eraser size={20}/></button>
                <div className="w-px h-6 bg-slate-200 mx-1" />
                <button onClick={handleUndo} className="p-3 text-slate-500 hover:bg-slate-100 rounded-lg"><RotateCcw size={20}/></button>
                <button onClick={handleRedo} className="p-3 text-slate-500 hover:bg-slate-100 rounded-lg"><RotateCw size={20}/></button>
              </div>

              <div className="flex items-center gap-6">
                <input type="range" min="1" max="20" value={strokeWidth} onChange={(e) => setStrokeWidth(parseInt(e.target.value))} className="w-24 accent-indigo-600" />
                <input type="color" value={penColor} onChange={(e) => {setPenColor(e.target.value); setIsEraser(false);}} className="w-10 h-10 rounded-lg cursor-pointer" />
                <button onClick={handleClearCanvas} className="text-rose-500 font-bold px-4 hover:bg-rose-50 rounded-xl py-2">Clear</button>
              </div>
            </div>

            <div className="flex-grow bg-slate-50/20">
              <ReactSketchCanvas
                ref={canvasRef}
                strokeWidth={strokeWidth}
                strokeColor={isEraser ? "#FFFFFF" : penColor}
                height="500px"
              />
              <button 
                onClick={handleSyncToAI} 
                disabled={isLoading} 
                className="absolute bottom-10 right-10 bg-indigo-600 text-white px-10 py-5 rounded-full font-black shadow-2xl flex items-center gap-3 hover:scale-105 active:scale-95 transition-all z-10"
              >
                {isLoading ? <Loader2 className="animate-spin" /> : <PlusCircle size={22} />}
                SYNC PAGE
              </button>
            </div>
          </>
        ) : (
          <div className="p-10 md:p-16 flex flex-col flex-grow bg-slate-50/30">
            <div className="flex justify-between items-center mb-12 border-b-2 border-slate-100 pb-8">
              <h2 className="text-5xl font-black text-slate-900 tracking-tighter">{activeTab}</h2>
              <button onClick={downloadPDF} className="bg-emerald-500 text-white px-8 py-4 rounded-full font-black shadow-lg hover:bg-emerald-600 transition-all flex items-center gap-2">
                <Download size={22}/> EXPORT PDF
              </button>
            </div>
            
            <div className="overflow-y-auto max-h-[600px] pr-4">
               {activeTab === "Notes" && renderNotes()}
               {activeTab === "Cheat Sheet" && renderCheatSheet()}
               {activeTab === "Quiz" && renderQuiz()}
            </div>
          </div>
        )}
      </main>
    </div>
  );
};

export default App;
