import React from "react";
import {
  BarChart, Bar,
  LineChart, Line,
  PieChart, Pie, Cell,
  XAxis, YAxis, CartesianGrid,
  Tooltip, Legend, ResponsiveContainer
} from "recharts";

const COLORS = [
  "#D30E8C", "#8B5CF6", "#4F93D9", "#00C49F",
  "#FFBB28", "#FF8042", "#c4b5fd", "#82CA9D",
  "#FFC658", "#f472b6"
];

const CustomTooltip = ({ active, payload, label }) => {
  if (active && payload && payload.length) {
    return (
      <div style={{
        background: "rgba(15, 15, 35, 0.95)",
        border: "1px solid rgba(139, 92, 246, 0.3)",
        borderRadius: "8px",
        padding: "10px 14px",
        color: "#fff",
        fontSize: "13px",
        boxShadow: "0 4px 20px rgba(0,0,0,0.3)"
      }}>
        <p style={{ color: "#8B5CF6", fontWeight: 600, marginBottom: 4 }}>{label}</p>
        {payload.map((entry, index) => (
          <p key={index} style={{ color: entry.color }}>
            {entry.name}: {typeof entry.value === "number"
              ? entry.value.toLocaleString()
              : entry.value}
          </p>
        ))}
      </div>
    );
  }
  return null;
};

function ChartRenderer({ chartType, chartData }) {
  if (!chartData || !chartData.labels || !chartData.values) {
    return null;
  }

  const data = chartData.labels.map((label, index) => ({
    name: label.length > 18 ? label.substring(0, 16) + "..." : label,
    fullName: label,
    value: chartData.values[index],
  }));

  const seriesName = chartData.series_name || "Value";

  if (chartType === "bar") {
    return (
      <ResponsiveContainer width="100%" height={320}>
        <BarChart data={data} margin={{ top: 20, right: 30, left: 20, bottom: 70 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="rgba(139, 92, 246, 0.1)" />
          <XAxis
            dataKey="name"
            tick={{ fill: "#8a8ab0", fontSize: 11 }}
            angle={-35}
            textAnchor="end"
            axisLine={{ stroke: "rgba(139, 92, 246, 0.2)" }}
            tickLine={{ stroke: "rgba(139, 92, 246, 0.2)" }}
          />
          <YAxis
            tick={{ fill: "#8a8ab0", fontSize: 11 }}
            axisLine={{ stroke: "rgba(139, 92, 246, 0.2)" }}
            tickLine={{ stroke: "rgba(139, 92, 246, 0.2)" }}
            tickFormatter={(value) => value.toLocaleString()}
          />
          <Tooltip content={<CustomTooltip />} />
          <Legend wrapperStyle={{ color: "#8a8ab0", fontSize: 12, paddingTop: 10 }} />
          <defs>
            <linearGradient id="barGradient" x1="0" y1="0" x2="0" y2="1">
              <stop offset="0%" stopColor="#D30E8C" stopOpacity={1} />
              <stop offset="100%" stopColor="#8B5CF6" stopOpacity={0.8} />
            </linearGradient>
          </defs>
          <Bar dataKey="value" name={seriesName} fill="url(#barGradient)" radius={[6, 6, 0, 0]} />
        </BarChart>
      </ResponsiveContainer>
    );
  }

  if (chartType === "line") {
    return (
      <ResponsiveContainer width="100%" height={320}>
        <LineChart data={data} margin={{ top: 20, right: 30, left: 20, bottom: 70 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="rgba(139, 92, 246, 0.1)" />
          <XAxis
            dataKey="name"
            tick={{ fill: "#8a8ab0", fontSize: 11 }}
            angle={-35}
            textAnchor="end"
            axisLine={{ stroke: "rgba(139, 92, 246, 0.2)" }}
            tickLine={{ stroke: "rgba(139, 92, 246, 0.2)" }}
          />
          <YAxis
            tick={{ fill: "#8a8ab0", fontSize: 11 }}
            axisLine={{ stroke: "rgba(139, 92, 246, 0.2)" }}
            tickLine={{ stroke: "rgba(139, 92, 246, 0.2)" }}
            tickFormatter={(value) => value.toLocaleString()}
          />
          <Tooltip content={<CustomTooltip />} />
          <Legend wrapperStyle={{ color: "#8a8ab0", fontSize: 12, paddingTop: 10 }} />
          <defs>
            <linearGradient id="lineGradient" x1="0" y1="0" x2="1" y2="0">
              <stop offset="0%" stopColor="#4F93D9" />
              <stop offset="100%" stopColor="#8B5CF6" />
            </linearGradient>
          </defs>
          <Line
            type="monotone"
            dataKey="value"
            name={seriesName}
            stroke="url(#lineGradient)"
            strokeWidth={3}
            dot={{ fill: "#8B5CF6", r: 5, strokeWidth: 2, stroke: "#1a1a3e" }}
            activeDot={{ r: 7, fill: "#D30E8C", stroke: "#fff", strokeWidth: 2 }}
          />
        </LineChart>
      </ResponsiveContainer>
    );
  }

  if (chartType === "pie") {
    return (
      <ResponsiveContainer width="100%" height={320}>
        <PieChart>
          <Pie
            data={data}
            cx="50%"
            cy="50%"
            labelLine={{ stroke: "#5a5a7e" }}
            label={({ name, percent }) =>
              name.length > 12
                ? (percent * 100).toFixed(1) + "%"
                : name + " " + (percent * 100).toFixed(1) + "%"
            }
            outerRadius={110}
            innerRadius={50}
            fill="#8884d8"
            dataKey="value"
            paddingAngle={2}
            stroke="rgba(15, 15, 35, 0.8)"
            strokeWidth={2}
          >
            {data.map((entry, index) => (
              <Cell key={index} fill={COLORS[index % COLORS.length]} />
            ))}
          </Pie>
          <Tooltip content={<CustomTooltip />} />
          <Legend wrapperStyle={{ color: "#8a8ab0", fontSize: 12 }} />
        </PieChart>
      </ResponsiveContainer>
    );
  }

  return <p style={{ color: "#7a7a9e" }}>Unsupported chart type: {chartType}</p>;
}

export default ChartRenderer;

