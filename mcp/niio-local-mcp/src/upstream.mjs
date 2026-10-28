import { currentHeaders } from './credentials.mjs';
import { Client } from '@modelcontextprotocol/sdk/client/index.js';
import { StreamableHTTPClientTransport } from '@modelcontextprotocol/sdk/client/streamableHttp.js';

export const UPSTREAM_URL = 'https://niiodemo.apsm.com.tw/mcp';

export async function connectUpstream({ headers: suppliedHeaders, url = UPSTREAM_URL } = {}) {
  if (![UPSTREAM_URL].includes(url)) throw new Error('UPSTREAM_DESTINATION_REJECTED');
  const destination = new URL(url);
  let authChallenge;
  const client = new Client({ name: 'niio-local-mcp-upstream', version: '0.1.0' });
  const transport = new StreamableHTTPClientTransport(new URL(url), {
    requestInit: { redirect: 'error' },
    fetch: async (url, init) => {
      if (new URL(url).href !== destination.href) throw new Error('UPSTREAM_DESTINATION_REJECTED');
      const headers = new Headers(init?.headers);
      headers.delete('Authorization');
      for (const [key, value] of Object.entries(suppliedHeaders ?? await currentHeaders())) headers.set(key, value);
      const response=await fetch(url, { ...init, headers, redirect: 'error' });
      if(response.status===401){
        const challenge=response.headers.get('www-authenticate');
        if(challenge&&/^Bearer\b/i.test(challenge)&&challenge.length<=2048&&!/[\r\n]/.test(challenge))authChallenge=challenge;
      }
      return response;
    }
  });
  try { await client.connect(transport); }
  catch (error) { if(authChallenge)error.authChallenge=authChallenge;await client.close().catch(()=>{}); throw error; }
  return { client, transport };
}
