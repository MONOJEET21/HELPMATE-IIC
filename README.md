# HelpMate² full-stack investor demo foundation

A parent platform with distinct HelpMate Hire and AgriBrain journeys.

## Included
- FastAPI + SQLAlchemy + SQLite
- JWT authentication and roles: customer, worker, farmer
- HelpMate jobs and applications API
- Worker profile API (skills, experience, location, expected salary, bio)
- AgriBrain farm records and GIS point map
- Sensor telemetry ingestion API
- ESP32 command queue: farmer queues commands, device polls, executes allow-listed command, acknowledges
- Crop image upload endpoint and clearly marked AI model integration placeholder
- Agricultural marketplace listing API
- React/Vite frontend with GIS, IoT controls, worker profile and AI upload pages
- ESP32 Arduino HTTP firmware template at `firmware/esp32_helpMate/esp32_helpMate.ino`

## Local setup (Windows PowerShell)
Backend terminal:
```powershell
cd backend
python -m venv .venv
.venv\\Scripts\\activate
pip install -r requirements.txt
copy .env.example .env
python -c "import secrets; print(secrets.token_hex(32))"
```
Put a generated value into SECRET_KEY and generate a different value for DEVICE_INGEST_KEY. Never commit `.env`.
```powershell
uvicorn app.main:app --reload
```
API docs: http://127.0.0.1:8000/docs

Frontend terminal:
```powershell
cd frontend
npm install
npm run dev
```
Set `frontend/.env` to `VITE_API_URL=http://127.0.0.1:8000`.

## Existing SQLite database warning
New SQLAlchemy tables are created on startup, but `create_all` does not alter existing tables. This package adds `device_commands` and `worker_profiles`. If the old database already exists, back it up first. For a disposable demo DB only, stop backend, rename `helpmate2.db` to a backup, then restart to create all tables. Do not delete a database containing data you need.

## ESP32 integration
Open `firmware/esp32_helpMate/esp32_helpMate.ino` in Arduino IDE. Install ArduinoJson library. Set Wi-Fi, API URL, device ID and same DEVICE_INGEST_KEY as backend. Implement the sensor read functions for the exact sensor models you own and calibrate them. Set farm_id if assigned. Firmware sends readings every 30s and polls command queue every 5s. It supports example PUMP_ON/OFF and VALVE_OPEN/CLOSE commands; wire relay pins only after checking your module's active level and electrical ratings.

Device endpoints:
- `POST /api/sensors/ingest` header `X-Device-Key`
- `GET /api/sensors/devices/{device_id}/commands` header `X-Device-Key`
- `POST /api/sensors/devices/{device_id}/commands/{command_id}/ack` header `X-Device-Key`
- Farmer dashboard queues via `POST /api/sensors/commands` with JWT.

## AI model integration
Replace `backend/app/ai.py`. Keep the `predict_crop_disease(file: UploadFile) -> dict` async contract or update the route accordingly. Load your trained model once at process startup, validate image types and dimensions, apply the exact training preprocessing, and return `status`, `prediction`, `confidence`, `severity`, and `recommendations`. Test on held-out field images. Current implementation only accepts/stores an image and returns placeholder status; it is not disease inference.

## Important honest limitations
This is a substantial working foundation, not a fully audited production system. Hardware drivers depend on your exact ESP32 board, sensor models, relay modules and wiring. Current GIS is farm-point mapping, not cadastral parcel polygons or satellite analytics. Marketplace provides listing API; online payments, delivery, dispute handling and AI recommendations need integration. Hiring has worker profiles and job/application APIs; identity verification, background checks, booking/payment and review moderation need operational integrations. Test every flow and secure deployment before sharing publicly.

## Deployment
Frontend: Vercel, root `frontend`, build `npm run build`, output `dist`, env `VITE_API_URL=https://YOUR-API`.
Backend: Render, root `backend`, build `pip install -r requirements.txt`, start `uvicorn app.main:app --host 0.0.0.0 --port $PORT`. Mount persistent disk `/var/data`, set `DATABASE_URL=sqlite:////var/data/helpmate2.db`, set `FRONTEND_ORIGIN` to exact Vercel URL. Persistent disk requires a paid Render service. Keep uploaded images on persistent storage or object storage. Use HTTPS and never expose device key to browser.

## HelpMate Hire + separate AgriBrain experience

- The HelpMate homepage links to `/agribrain` in a new browser tab.
- AgriBrain has its own farmer-facing landing page and navigation under `/agribrain/*`.
- Farmer sign-up is preselected from AgriBrain links (`/register?role=farmer`).
- HelpMate Hire supports customer job posting (`POST /api/jobs`), public job browsing, worker applications (`POST /api/jobs/{id}/apply`), worker profile creation, and employer-side worker discovery (`GET /api/workers`).
- Worker contact details are displayed to signed-in hiring customers when available. Obtain worker consent and add verification/privacy controls before public production launch.

### Important implementation limits

This is an expanded working prototype, not a production-verified hiring marketplace. The frontend build and full end-to-end tests must be run on your machine after `npm install`. AgriBrain's crop AI route is still an integration placeholder until your trained model is connected. The marketplace and sensor routes retain their prototype limitations described above.
