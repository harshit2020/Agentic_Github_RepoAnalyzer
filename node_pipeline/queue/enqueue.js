import axios from 'axios';
import repo_job_queue from './queue.js';
import asyncHandler from '../utils/asyncHandler.js'

const enqueue_user_setup = asyncHandler(async(req, res) => {
    const user_id = req.userId || "test_mail@gmail.com";
    const { db_flag, ollama_flag, repo_url, modelName, api_key } = req.body

    let db_job

    if(db_flag == true) {
        const { db_host, db_port } = req.body
        db_job = await repo_job_queue.add('chroma-setup', {
            endpoint: "/api/v1/db_setup_offline",
            method: "POST",
            db_host,
            db_port,
            user_id
        },{ removeOnComplete: 1000, removeOnFail: 5000 })
    } else {
        const { CHROMA_API_KEY, CHROMA_TENANT, CHROMA_DATABASE, CHROMA_HOST } = req.body
        db_job = await repo_job_queue.add('chroma-setup', {
            endpoint: "/api/v1/db_setup_online",
            method: "POST",
            CHROMA_API_KEY,
            CHROMA_HOST,
            CHROMA_TENANT,
            CHROMA_DATABASE,
            user_id
        },{ removeOnComplete: 1000, removeOnFail: 5000 })
    }

    if(ollama_flag == true) {
        const { ollama_host, ollama_port, num_ctx, num_predict,
                temperature, requests_per_second, max_bucket_size, model_name } = req.body

        const ollama_job = await repo_job_queue.add('ollama-setup', {
            endpoint: "/api/v1/ollama_setup",
            method: "POST",
            user_id,
            ollama_host,
            ollama_port,
            num_ctx,
            num_predict,
            temperature,
            requests_per_second,
            max_bucket_size,
            model_name
        },{ removeOnComplete: 1000, removeOnFail: 5000 })

        const job = await repo_job_queue.add('user-redis-setup', {
            endpoint: "/api/v1/user_setup",
            method: "POST",
            user_id,
            db_flag,
            ollama_flag,
            repo_url,
            modelName,
            api_key
        },{ removeOnComplete: 1000, removeOnFail: 5000 })
        console.log(job.data)
        console.log("================================================================================")
        console.log(db_job.data)
        console.log("================================================================================")
        console.log(ollama_job.data)
        return res.json({
            jobID: job.id,
            sub_dbJob: db_job.id,
            sub_ollama_job: ollama_job.id,
            status: "queued"
        })
    }

    const job = await repo_job_queue.add('user-redis-setup', {
        endpoint: "/api/v1/user_setup",
        method: "POST",
        user_id,
        db_flag,
        ollama_flag,
        repo_url,
        modelName,
        api_key
    })
    console.log(job.data)
    console.log("================================================================================")
    console.log(db_job.data)
    return res.json({
        jobID: job.id,
        sub_dbJob: db_job.id,
        status: "queued"
    },{ removeOnComplete: 1000, removeOnFail: 5000 })
})

const enqueue_indexer = asyncHandler(async(req, res) => {
    const user_id = req.userId || "test_mail@gmail.com";
    const job = await repo_job_queue.add('index', {
        endpoint: "/api/v1/indexer",
        method: "GET",
        user_id
    },{ removeOnComplete: 1000, removeOnFail: 5000 })
    console.log(job.data)
    return res.json({ jobID: job.id,status: "queued" })
})

const enqueue_ai_retrieval = asyncHandler(async(req, res) => {
     const user_id = req.userId || "test_mail@gmail.com";
    const { user_query } = req.body
    const job = await repo_job_queue.add('ai-retrieval', {
        endpoint: "/api/v1/ai_retrieval_query",
        method: "GET",
        user_id,
        user_query
    },{ removeOnComplete: 1000, removeOnFail: 5000 })
    console.log(job.data)
    return res.json({ jobID: job.id, status: "queued" })
})

const healthCheckJob = asyncHandler(async(req, res) => {
    const job = await repo_job_queue.getJob(req.params.jobID)
    if(!job) {
        return res.status(404).json({ error: "Job not found" })
    }
    const status = await job.getState()   
    const result = job.returnvalue        
    const failed = job.failedReason       
    console.log(job.data)
    return res.status(200).json({
        jobID: req.params.jobID,
        state: status,
        result,
        error: failed
    })
})

export { 
        enqueue_user_setup, 
        enqueue_indexer,
        enqueue_ai_retrieval,
        healthCheckJob 
    }