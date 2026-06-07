import { Router } from "express";
import {enqueue_indexer, enqueue_ai_retrieval} from '../queue/enqueue.js'

const enq_ret_router = Router();

enq_ret_router.route("/index").post(enqueue_indexer);
enq_ret_router.route("/retrieve").get(enqueue_ai_retrieval);

export default enq_ret_router


