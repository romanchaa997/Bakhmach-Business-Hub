import express from "express";
import cors from "cors";
import helmet from "helmet";
import morgan from "morgan";
import goalsRouter from "./routes/goalsRoutes";
import tasksRouter from "./routes/tasksRoutes";

const app = express();

app.use(helmet());
app.use(cors());
app.use(express.json());
app.use(morgan("combined"));

app.use("/api/v1/goals", goalsRouter);
app.use("/api/v1/tasks", tasksRouter);

// basic health check for monitoring
app.get("/health", (_req, res) => {
  res.json({ status: "ok", service: "goals-tasks" });
});

const PORT = process.env.PORT || 4002;
app.listen(PORT, () => {
  console.log(`Goals+Tasks service listening on port ${PORT}`);
});
