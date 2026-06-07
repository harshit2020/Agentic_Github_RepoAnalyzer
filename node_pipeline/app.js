import express from 'express';
import upload from "./utils/multer_setup.js"

const app = express()


import user_router from './routes/user_setup_route.js'
import enq_ret_router from './routes/indexer_retrieval_route.js'

app.use("/api/v1/users",upload.none(),user_router)
app.use("/api/v1/repo_operation",upload.none(),enq_ret_router)

export default app
