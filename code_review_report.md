# Code Review Report / 代码审查报告

## 1) Scope / 审查范围
- Workspace scanned: `c:\Users\24228\Desktop\smart_media`
- Focused review targets: backend API/auth/security paths, proxy/streaming chain, config and secret handling, frontend credential storage.
- Evidence-based review with file+line references.

## 2) Executive Summary / 结论摘要
- Critical issues found: **4**
- High issues found: **2**
- Medium issues found: **2**
- Primary risk theme: **authentication coverage mismatch + sensitive data exposure**.

## 3) Findings (By Severity) / 问题清单（按严重级别）

### Critical-1: Security config can require API key, but most sensitive endpoints are not actually protected
- EN: `security.require_api_key` defaults to true, but many operational endpoints do not enforce `Depends(require_api_key)`. This creates a false sense of protection and allows unauthenticated access paths.
- 中文：配置层默认要求 API Key，但大量接口未绑定鉴权依赖，形成“看似开启安全、实则未生效”的高风险错配。
- Evidence:
  - `quark_strm/app/config/settings.py:403` (`require_api_key` default true)
  - `quark_strm/app/core/dependencies.py:34` (`require_api_key` implementation)
  - `quark_strm/app/api/proxy.py:49` (`/stream/{file_id}` no auth)
  - `quark_strm/app/api/proxy.py:180` (`/redirect/{file_id}` no auth)
  - `quark_strm/app/api/proxy.py:252` (`/transcoding/{file_id}` no auth)
  - `quark_strm/app/api/proxy.py:331` (`clear_cache` is protected, inconsistent)
- Impact: Unauthenticated callers can trigger link resolution/streaming behaviors and consume backend resources.

### Critical-2: Notification read APIs expose channel config without auth
- EN: Read endpoints for channels/rules/logs are public, while write endpoints are protected. Channel response includes raw `config: dict`, which may contain bot tokens/webhooks.
- 中文：通知模块“写接口有鉴权、读接口无鉴权”，且返回结构含 `config`，可能直接暴露密钥/Webhook。
- Evidence:
  - `quark_strm/app/api/notification.py:93` (`GET /channels`)
  - `quark_strm/app/api/notification.py:94` (`list_channels` without `Depends(require_api_key)`)
  - `quark_strm/app/api/notification.py:34`
  - `quark_strm/app/api/notification.py:41` (`ChannelResponse.config: dict`)
  - `quark_strm/app/api/notification.py:195`, `quark_strm/app/api/notification.py:196` (`GET /rules` public)
  - `quark_strm/app/api/notification.py:220`, `quark_strm/app/api/notification.py:221` (`GET /logs` public)
- Impact: Potential credential disclosure and operational metadata leak.

### Critical-3: WebDAV service falls back to default credentials `admin/password`
- EN: Runtime fallback credentials are hardcoded if config values are empty.
- 中文：WebDAV 运行时存在硬编码兜底账号密码，配置缺失时会启用弱口令。
- Evidence:
  - `quark_strm/app/services/webdav/service.py:23`
  - `quark_strm/app/services/webdav/service.py:24`
- Impact: Unauthorized access risk in misconfigured deployments.

### Critical-4: Frontend initializes WebDAV with insecure defaults and no backend persistence wired
- EN: UI defaults are `enabled: true`, `username: admin`, `password: password`; loading/saving are TODO stubs.
- 中文：前端默认值直接是弱口令且默认启用，且“加载/保存配置”未接后端，易导致误配置被长期忽略。
- Evidence:
  - `quark_strm/web/src/views/WebDAVView.vue:171`
  - `quark_strm/web/src/views/WebDAVView.vue:173`
  - `quark_strm/web/src/views/WebDAVView.vue:174`
  - `quark_strm/web/src/views/WebDAVView.vue:206`
  - `quark_strm/web/src/views/WebDAVView.vue:225`
- Impact: Operational security drift and accidental exposure.

### High-1: Proxy stream endpoint forcibly sets wildcard CORS header
- EN: Stream response injects `Access-Control-Allow-Origin: *`, bypassing centralized CORS policy intent.
- 中文：流媒体代理强制写入 `*` 跨域头，破坏统一 CORS 策略边界。
- Evidence:
  - `quark_strm/app/api/proxy.py:148`
- Impact: Cross-origin abuse surface increases for hotlink/stream endpoints.

### High-2: Client stores auth secrets in `localStorage`
- EN: Bearer token/API key are read from `localStorage`, which is vulnerable under XSS.
- 中文：令牌与 API Key 保存在 `localStorage`，一旦 XSS 即可被窃取。
- Evidence:
  - `quark_strm/web/src/api/index.ts:13`
  - `quark_strm/web/src/api/index.ts:17`
- Impact: Session takeover and API abuse after script injection.

### Medium-1: `/config` endpoint exposes runtime configuration metadata without auth
- EN: Root config endpoint returns database path and endpoint count publicly.
- 中文：`/config` 无鉴权返回部分运行配置元信息。
- Evidence:
  - `quark_strm/app/main.py:337`
  - `quark_strm/app/main.py:344`
  - `quark_strm/app/main.py:349`
- Impact: Information disclosure that helps attackers profile deployment.

### Medium-2: Broad exception capture pattern in critical paths reduces diagnosability and control
- EN: Many API/service paths use `except Exception` and rethrow generic HTTP 500; this can hide root causes and produce inconsistent error semantics.
- 中文：关键路径大量 `except Exception`，导致错误语义弱化、排障成本上升。
- Evidence samples:
  - `quark_strm/app/api/proxy.py` (multiple broad catches)
  - `quark_strm/app/main.py` (startup/monitoring broad catches)
- Impact: Reliability and operability risk (not direct exploit by itself).

## 4) Positive Notes / 正向观察
- Input validation utility exists and blocks common traversal/scheme abuse patterns (`quark_strm/app/core/validators.py`).
- API key dependency uses constant-time comparison (`quark_strm/app/core/dependencies.py`).

## 5) Recommended Remediation Order / 修复优先级建议
1. Enforce auth consistently for all sensitive read/write/stream/proxy endpoints; consider router-level dependency defaults.
2. Protect notification read endpoints and mask or remove secrets from response models.
3. Remove all default credentials (`admin/password`) and fail fast when required credentials are absent.
4. Remove wildcard CORS override in proxy stream path; rely on centralized policy.
5. Replace `localStorage` secrets with HTTP-only secure cookies or short-lived in-memory/session strategy.
6. Gate `/config` behind auth or reduce output to minimal health metadata.

## 6) Testing Gaps / 测试缺口
- No evidence of negative tests verifying unauthorized access is rejected for proxy and notification read endpoints.
- Add explicit auth matrix tests (authorized vs unauthorized) for:
  - `/api/proxy/*`
  - `/api/notification/*`
  - `/config` and system config surfaces

## 7) Final Assessment / 最终评估
- Current posture: **Not production-safe without security hardening**.
- Main blocker: **authentication and secret exposure inconsistencies**.
