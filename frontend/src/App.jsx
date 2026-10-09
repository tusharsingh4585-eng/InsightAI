import { useState } from "react";
import { Upload, Sparkles, Database, TrendingUp, DollarSign, FileSpreadsheet, AlertCircle } from "lucide-react";
import { ResponsiveContainer, LineChart, Line, XAxis, YAxis, Tooltip, CartesianGrid } from "recharts";

const API = "http://localhost:8000/api";

function formatMoney(value) {
  return new Intl.NumberFormat("en-IN", { maximumFractionDigits: 0 }).format(value || 0);
}

export default function App() {
  const [result, setResult] = useState(null);
  const [fileName, setFileName] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  async function handleUpload(event) {
    const file = event.target.files?.[0];
    if (!file) return;

    setFileName(file.name);
    setError("");
    setLoading(true);

    const form = new FormData();
    form.append("file", file);

    try {
      const response = await fetch(`${API}/datasets/analyze`, {
        method: "POST",
        body: form
      });

      const data = await response.json();
      if (!response.ok) throw new Error(data.detail || "Analysis failed");
      setResult(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="app-shell">
      <aside className="sidebar">
        <div className="brand"><Sparkles size={20}/> InsightAI</div>
        <nav>
          <span className="active">Overview</span>
          <span>Analytics</span>
          <span>Datasets</span>
          <span>AI Insights</span>
        </nav>
        <div className="side-footer">Business Intelligence<br/>v1.0</div>
      </aside>

      <main className="main">
        <header className="topbar">
          <div>
            <p className="eyebrow">AI-POWERED BUSINESS INTELLIGENCE</p>
            <h1>Turn data into decisions.</h1>
            <p className="sub">Upload a sales CSV and get instant KPIs, trends and actionable insights.</p>
          </div>
          <label className="upload-btn">
            <Upload size={18}/>
            {loading ? "Analyzing..." : "Upload CSV"}
            <input type="file" accept=".csv" onChange={handleUpload} hidden />
          </label>
        </header>

        {error && <div className="error"><AlertCircle size={18}/>{error}</div>}

        <section className="kpis">
          <Kpi icon={<DollarSign/>} label="Revenue" value={result ? `₹${formatMoney(result.summary.revenue_total)}` : "—"} />
          <Kpi icon={<TrendingUp/>} label="Profit" value={result ? `₹${formatMoney(result.summary.profit_total)}` : "—"} />
          <Kpi icon={<Database/>} label="Rows Analyzed" value={result ? result.summary.rows.toLocaleString() : "—"} />
          <Kpi icon={<FileSpreadsheet/>} label="Profit Margin" value={result ? `${result.summary.profit_margin}%` : "—"} />
        </section>

        <section className="grid">
          <div className="card chart-card">
            <div className="card-head">
              <div><h2>Revenue Trend</h2><span>{fileName || "Upload a dataset to populate analytics"}</span></div>
            </div>
            {result?.trend?.length ? (
              <ResponsiveContainer width="100%" height={300}>
                <LineChart data={result.trend}>
                  <CartesianGrid strokeDasharray="3 3" vertical={false}/>
                  <XAxis dataKey="date"/>
                  <YAxis/>
                  <Tooltip/>
                  <Line type="monotone" dataKey="revenue" strokeWidth={3} dot={false}/>
                </LineChart>
              </ResponsiveContainer>
            ) : (
              <div className="empty"><TrendingUp size={42}/><p>Monthly revenue trend will appear here.</p></div>
            )}
          </div>

          <div className="card">
            <div className="card-head"><div><h2>AI Insights</h2><span>Automated data interpretation</span></div><Sparkles size={20}/></div>
            <div className="insights">
              {result?.insights?.length ? result.insights.map((item, i) => (
                <div className="insight" key={i}><span>{String(i + 1).padStart(2, "0")}</span><p>{item}</p></div>
              )) : (
                <div className="empty"><Sparkles size={42}/><p>Upload data to generate business insights.</p></div>
              )}
            </div>
          </div>
        </section>

        <section className="card">
          <div className="card-head"><div><h2>Dataset Profile</h2><span>Schema detected from uploaded CSV</span></div></div>
          <div className="tags">
            {result?.summary?.columns_list?.length
              ? result.summary.columns_list.map(col => <span key={col}>{col}</span>)
              : <span className="muted">No dataset loaded</span>}
          </div>
        </section>
      </main>
    </div>
  );
}

function Kpi({ icon, label, value }) {
  return <div className="kpi"><div className="kpi-icon">{icon}</div><div><span>{label}</span><strong>{value}</strong></div></div>;
}
