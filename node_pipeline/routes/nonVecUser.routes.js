import { Router } from "express";
import {registerUser, loginUser, changeCurrentPassword,changeAvatar,deleteAvatar} from '../contollers/user.controller.js'
import upload from "../utils/multer_setup.js"

const user_nonVecRouter = Router();

user_nonVecRouter.route("/signup").post(upload.fields([
    {
        name:"avatar",
        maxCount:1
    }
])
    ,registerUser);
user_nonVecRouter.route("/login").post(upload.none(),loginUser);
user_nonVecRouter.route("/change_password").post(upload.none(),changeCurrentPassword);
user_nonVecRouter.route("/change_avatar").post(upload.fields([
    {
        name:"avatar",
        maxCount:1
    }
]),changeAvatar);
user_nonVecRouter.route("/delete_avatar").post(upload.none(),deleteAvatar);

export default user_nonVecRouter

