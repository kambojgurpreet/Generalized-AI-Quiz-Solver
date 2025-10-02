@echo off
echo Stopping AI Quiz Solver Docker services...
docker-compose -f docker-compose.dev.yml down
echo.
echo Services stopped.
pause