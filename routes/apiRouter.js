import { Router } from "express";
import fs from "fs";
import path from "path";
const apiRouter = Router();
import jwt from "jsonwebtoken";
import FormData from "form-data";
import { handleFileUpload } from "../middlewares/upload.js";
import multer from "multer";
import httpProxy from "http-proxy";

const { createProxyServer } = httpProxy;
const proxy = createProxyServer({});

const storage = multer.diskStorage({
    destination: "uploads/",
    filename: (req, file, cb) => {
        const ext = path.extname(file.originalname);
        cb(null, `${file.fieldname}-${Date.now()}${ext}`);
    },
});

const upload = multer({ storage });

apiRouter.get('/', (req, res) => {
    return res.json({
        success: true,
        status: "success",
        statusCode: 200,
        message: "API is working correctly"
    });
});

const authMiddleware = (req, res, next) => {
    const authHeader = req.headers.authorization;

    if (!authHeader) {
        return res.status(401).json({
            success: false,
            status: "error",
            statusCode: 401,
            message: "Authorization header missing"
        });
    }

    const token = authHeader.split(' ')[1];

    if (!token) {
        return res.status(401).json({
            success: false,
            status: "error",
            statusCode: 401,
            message: "Token missing"
        });
    }

    try {
        const decoded = jwt.verify(token, process.env.JWT_SECRET);
        req.user = decoded;
        next();
    } catch (error) {
        return res.status(401).json({
            success: false,
            status: "error",
            statusCode: 401,
            message: "Invalid token"
        });
    }
};

apiRouter.post("/signup", async (req, res) => {
    const { username, password } = req.body;

    const filPath = path.join(process.cwd(), "data", "data.json");
    const data = await fs.readFileSync(filPath, "utf-8")
    const usersData = JSON.parse(data);

    const existingUser = usersData.find(user => user.username === username);

    if (existingUser) {
        return res.status(409).json({
            success: false,
            status: "error",
            statusCode: 409,
            message: "Username already exists"
        });
    }

    const newUser = { username, password, id: Date.now() };
    usersData.push(newUser);

    await fs.writeFileSync(filPath, JSON.stringify(usersData, null, 2));

    return res.status(201).json({
        success: true,
        status: "success",
        statusCode: 201,
        message: "User registered successfully",
        newUser
    });
});

apiRouter.post("/login", async (req, res) => {
    const { username, password } = req.body;

    const filPath = path.join(process.cwd(), "data", "data.json");
    const data = await fs.readFileSync(filPath, "utf-8")
    const usersData = JSON.parse(data);

    const newUser = usersData.find(user => user.username === username && user.password === password);

    if (!newUser) {
        return res.status(401).json({
            success: false,
            status: "error",
            statusCode: 401,
            message: "Invalid username or password"
        });
    }

    const jwtToken = jwt.sign({ id: newUser.id }, process.env.JWT_SECRET, { expiresIn: '20d' });

    return res.json({
        success: true,
        status: "success",
        statusCode: 200,
        message: "User logged in successfully",
        token: jwtToken,
    });
});

apiRouter.post("/fert-model", authMiddleware, async (req, res) => {

    let data = null;
    try {

        const response = await fetch("http://localhost:8000/predict", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify(req.body),
        })
        data = await response.json();

    } catch (error) {
        return res.status(500).json({
            success: false,
            status: "error",
            statusCode: 500,
            message: "Failed to fetch data from ML model"
        });
    }

    return res.json({
        success: true,
        status: "success",
        statusCode: 200,
        message: "AI endpoint hit successfully",
        data,
    });
});

apiRouter.post(
    "/soil-type-model",
    authMiddleware,
    (req, res) => {
        req.url = "/predict";
        proxy.web(req, res, { target: "http://127.0.0.1:8001" });
    }
);

export default apiRouter;