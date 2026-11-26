---
updatedAt: 2026-08-18T10:11:33.000Z
agentTools:
  projectIndex: https://docs.capillarytech.com/llms.txt
---

# Web SDK

<HTMLBlock>{`
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Web SDK</title>
    <style>
        *, *::before, *::after {
            box-sizing: border-box;
            margin: 0;
            padding: 0;
        }

        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell;
            line-height: 1.6;
        }

        .nav-list {
            list-style: none;
            padding: 0;
            margin: 0;
        }

        .nav-item {
            padding: 12px 16px;
            border-radius: 8px;
            margin: 8px 0;
            transition: all 0.2s ease;
            background: #D8EDFF;
            border: 1px solid #A8CFEE;
            position: relative;
            overflow: hidden;
        }

        .nav-item::before {
            content: '';
            position: absolute;
            left: 0;
            top: 0;
            bottom: 0;
            width: 3px;
            background: #2466EA;
            transform: scaleX(0);
            transform-origin: left;
            transition: transform 0.15s ease;
        }

        .nav-item:hover {
            background: #BFE0F7;
            transform: translateX(4px);
            border-color: #2466EA;
        }

        .nav-item:hover::before {
            transform: scaleX(1);
        }

        .nav-link {
            text-decoration: none !important;
            display: block;
            font-size: 16px;
            font-weight: 700;
            color: #091E42;
            transition: color 0.15s ease;
        }

        .nav-link:hover {
            color: #2466EA;
        }
    </style>
</head>
<body>
    <ul class="nav-list">
        <li class="nav-item"><a href="https://docs.capillarytech.com/docs/web-sdk-getting-started#/" class="nav-link">Getting Started</a></li>
        <li class="nav-item"><a href="https://docs.capillarytech.com/docs/web-sdk-ai-integration-guide#/" class="nav-link">AI-Assisted Integration Guide</a></li>
        <li class="nav-item"><a href="https://docs.capillarytech.com/docs/web-sdk-install#/" class="nav-link">Install SDK</a></li>
        <li class="nav-item"><a href="https://docs.capillarytech.com/docs/web-sdk-initialisation#/" class="nav-link">Initialise SDK</a></li>
        <li class="nav-item"><a href="https://docs.capillarytech.com/docs/configure-firebase-web#/" class="nav-link">Configure Firebase</a></li>
        <li class="nav-item"><a href="https://docs.capillarytech.com/docs/push-notification-web#/" class="nav-link">Configure Push Notifications</a></li>
        <li class="nav-item"><a href="https://docs.capillarytech.com/docs/gamification-web#/" class="nav-link">Configure Gamification (Experience+)</a></li>
        <li class="nav-item"><a href="https://docs.capillarytech.com/docs/web-sdk-api-reference#/" class="nav-link">API Reference for Event Tracking, Notifications, and User Lifecycle</a></li>
        <li class="nav-item"><a href="https://docs.capillarytech.com/docs/web-sdk-troubleshooting#/" class="nav-link">Validation, Troubleshooting &amp; Rollback</a></li>
    </ul>
</body>
</html>
`}</HTMLBlock>

<br />