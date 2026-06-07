import { Worker } from "bullmq";
import axios from "axios";
import redis_connection from "../config/redis.js";

const internalClient = axios.create({
    baseURL : process.env.FASTAPI_INTERNAL_URL,
    headers : {'X-INTERNAL-KEY':process.env.INTERNAL_API_KEY}
})

const worker = new Worker('repo_job',async(job)=>{
    const{endpoint,method, ...payload} = job.data
    console.log(`[${job.name}] job ${job.id} → ${method.toLowerCase()} ${endpoint}`)
    const strr = "?userId=test_mail@gmail.com"
    console.log(process.env.FASTAPI_INTERNAL_URL + endpoint+strr)
    await job.updateProgress(10)

   const config = {
        method: method.toLowerCase(),
        url: endpoint,
        baseURL: process.env.FASTAPI_INTERNAL_URL,
        params: method.toLowerCase() === "get" ? payload : undefined,
        data: method.toLowerCase() !== "get" ? payload : undefined
    };

    const response = await internalClient.request(config);

    await job.updateProgress(100)
    return response.data
},redis_connection)

worker.on('completed', (job) => {
    console.log(`[${job.name}] job ${job.id} completed`)
})

worker.on('failed', (job, err) => {
    console.error(`[${job.name}] job ${job.id} failed: ${err.message}`)
})

export default worker