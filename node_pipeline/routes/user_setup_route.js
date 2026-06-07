import { Router } from "express";
import {enqueue_user_setup, healthCheckJob} from '../queue/enqueue.js'


const user_router = Router();

user_router.route("/user_setup").post(enqueue_user_setup);
user_router.route("/healthCheck/:jobID").get(healthCheckJob);

export default user_router


