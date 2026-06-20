import { Router } from "express";
import {enqueue_indexer, enqueue_ai_retrieval} from '../queue/enqueue.js'
import upload from "../utils/multer_setup.js"

const enq_ret_router = Router();

enq_ret_router.route("/index").post(upload.none(),enqueue_indexer);
enq_ret_router.route("/retrieve").post(upload.none(),enqueue_ai_retrieval);

export default enq_ret_router


