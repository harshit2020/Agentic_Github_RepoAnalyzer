import express from 'express';
import cors from 'cors';

const app = express()

//app config
app.use(
  cors({
    origin: "http://localhost:5173",
    credentials: true,
  })
);
app.use(express.json());


import user_router from './routes/user_setup_route.js'
import enq_ret_router from './routes/indexer_retrieval_route.js'
import user_nonVecRouter from './routes/nonVecUser.routes.js'
import model_router from './routes/model.routes.js'

app.use("/api/v1/users",user_router)
app.use("/api/v1/repo_operation",enq_ret_router)
app.use("/api/v1/users_nonVecDB",user_nonVecRouter)
app.use("/api/v1/models",model_router)
export default app
