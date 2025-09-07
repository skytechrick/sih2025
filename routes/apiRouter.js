import { Router } from "express";

const apiRouter = Router();

apiRouter.get('/', (req, res) => {
    return res.json({
        success: true,
        status: "success",
        statusCode: 200,
        message: "API is working correctly"
    });
});

export default apiRouter;