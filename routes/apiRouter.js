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

apiRouter.post("/model", async (req, res) => {
    const { lat, long } = req.body;
    console.log(lat, long);
    let data = null;
    try {

        // const response = await fetch({})
        // data = await response.json();

    } catch (error) {
        console.error("Error fetching data from AI model:", error);
        return res.status(500).json({
            success: false,
            status: "error",
            statusCode: 500,
            message: "Failed to fetch data from AI model"
        });
    }

    return res.json({
        success: true,
        status: "success",
        statusCode: 200,
        message: "AI endpoint hit successfully"
        // response,
    });
});

export default apiRouter;