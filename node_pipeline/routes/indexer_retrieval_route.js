import { Router } from "express";
import {enqueue_indexer, enqueue_ai_retrieval} from '../queue/enqueue.js'
import {get_user_setup, get_indexed_repos, check_indexed_repos} from '../contollers/py_pipeline.contoller.js'
import upload from "../utils/multer_setup.js"

const enq_ret_router = Router();

enq_ret_router.route("/index").post(upload.none(),enqueue_indexer);
enq_ret_router.route("/retrieve").post(upload.none(),enqueue_ai_retrieval);
enq_ret_router.route("/user_indexed_repos").post(upload.none(),get_indexed_repos);
enq_ret_router.route("/checkExistingRepo").post(upload.none(),check_indexed_repos);

export default enq_ret_router


