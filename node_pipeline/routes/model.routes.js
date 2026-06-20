import { Router } from "express";
import {get_model_names} from '../contollers/py_pipeline.contoller.js'


const model_router = Router();

model_router.route("/getModelNames").get(get_model_names)

export default model_router


