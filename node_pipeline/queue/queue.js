import {Queue} from 'bullmq';
import redis_connection from '../config/redis.js'

const repo_job_queue = new Queue('repo_job',redis_connection)
export default repo_job_queue