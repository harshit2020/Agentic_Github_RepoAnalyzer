import { Router } from "express";
import {enqueue_user_setup, healthCheckJob} from '../queue/enqueue.js'
import {get_user_setup, get_indexed_repos} from '../contollers/py_pipeline.contoller.js'
import upload from "../utils/multer_setup.js"

const user_router = Router();

user_router.route("/user_setup").post(upload.none(),enqueue_user_setup);
user_router.route("/user_setup").get(upload.none(),get_user_setup);
user_router.route("/user_indexed_repos").get(upload.none(),get_indexed_repos);
user_router.route("/healthCheck/:jobID").get(upload.none(),healthCheckJob);

export default user_router


