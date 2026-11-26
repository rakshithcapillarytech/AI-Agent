---
updatedAt: 2026-11-17T05:59:58.000Z
agentTools:
  projectIndex: https://docs.capillarytech.com/llms.txt
---

# Install SDK

This section provides information on how to install the SDK.

# Choose a release channel

| Channel                                | When to use                                                      |
| -------------------------------------- | ---------------------------------------------------------------- |
| **Production** (`@latest`) — *default* | production environments — stable, fully tested releases          |
| **Beta** (`@beta`)                     | pre-release testing — latest features before the next stable cut |

# Install the package

Install based on your package manager:

| Lock file present   | Production                      | Beta                                 |
| ------------------- | ------------------------------- | ------------------------------------ |
| `package-lock.json` | `npm install cap-hydra-web-sdk` | `npm install cap-hydra-web-sdk@beta` |
| `yarn.lock`         | `yarn add cap-hydra-web-sdk`    | `yarn add cap-hydra-web-sdk@beta`    |
| `pnpm-lock.yaml`    | `pnpm add cap-hydra-web-sdk`    | `pnpm add cap-hydra-web-sdk@beta`    |
| `bun.lockb`         | `bun add cap-hydra-web-sdk`     | `bun add cap-hydra-web-sdk@beta`     |
| None detected       | `npm install cap-hydra-web-sdk` | `npm install cap-hydra-web-sdk@beta` |

Once installed, continue to [Initialise SDK](https://docs.capillarytech.com/docs/web-sdk-initialisation).