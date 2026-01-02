import puppeteer from 'puppeteer';
import path from 'path';
import { createWriteStream } from 'fs';
import { promises as fs } from 'fs';

interface ExportOptions {
  format: 'executive' | 'technical' | 'usecase' | 'prospectus' | 'complete';
  includeCharts?: boolean;
  includeMetrics?: boolean;
  theme?: 'light' | 'dark';
}

interface ArchitectureData {
  nodes: Array<{ id: string; name: string; health: number; readiness: number }>;
  edges: Array<{ source: string; target: string; latency: number }>;
  usesCases?: Array<{ id: string; title: string; traffic: string }>;
}

class PDFExportService {
  private browser: any;

  async initialize() {
    this.browser = await puppeteer.launch({
      headless: 'new',
      args: ['--no-sandbox'],
    });
  }

  async exportArchitecture(data: ArchitectureData, options: ExportOptions): Promise<Buffer> {
    if (!this.browser) await this.initialize();

    const page = await this.browser.newPage();
    await page.setViewport({ width: 1200, height: 1600 });

    const htmlContent = this.generateHTML(data, options);
    await page.setContent(htmlContent, { waitUntil: 'networkidle0' });

    const pdfBuffer = await page.pdf({
      format: 'A4',
      margin: { top: '1cm', right: '1cm', bottom: '1cm', left: '1cm' },
      printBackground: true,
    });

    await page.close();
    return pdfBuffer;
  }

  private generateHTML(data: ArchitectureData, options: ExportOptions): string {
    const pageCount = this.getPageCount(options.format);
    const htmlTemplate = `
      <!DOCTYPE html>
      <html>
        <head>
          <meta charset="UTF-8">
          <style>
            * { margin: 0; padding: 0; box-sizing: border-box; }
            body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; line-height: 1.6; }
            .container { max-width: 100%; margin: 0 auto; }
            .page { page-break-after: always; padding: 2cm; background: ${options.theme === 'dark' ? '#1a1a1a' : '#fff'}; color: ${options.theme === 'dark' ? '#fff' : '#000'}; }
            .header { border-bottom: 3px solid #2563eb; margin-bottom: 2rem; padding-bottom: 1rem; }
            h1 { font-size: 2.5rem; margin-bottom: 0.5rem; }
            h2 { font-size: 1.8rem; margin-top: 2rem; margin-bottom: 1rem; }
            h3 { font-size: 1.3rem; margin-top: 1.5rem; margin-bottom: 0.8rem; }
            .metrics { display: grid; grid-template-columns: 1fr 1fr; gap: 1rem; margin: 1.5rem 0; }
            .metric-box { border: 2px solid #2563eb; padding: 1rem; border-radius: 8px; }
            .metric-value { font-size: 2rem; font-weight: bold; color: #2563eb; }
            table { width: 100%; border-collapse: collapse; margin: 1rem 0; }
            th, td { border: 1px solid #ddd; padding: 0.75rem; text-align: left; }
            th { background-color: #2563eb; color: white; }
            .health-bar { width: 100%; height: 20px; background: #e0e0e0; border-radius: 10px; overflow: hidden; }
            .health-fill { height: 100%; background: linear-gradient(to right, #dc2626, #eab308, #16a34a); }
            .footer { margin-top: 2rem; padding-top: 1rem; border-top: 1px solid #ddd; font-size: 0.9rem; color: #666; }
          </style>
        </head>
        <body>
          <div class="container">
            ${this.generatePages(data, options)}
          </div>
        </body>
      </html>
    `;
    return htmlTemplate;
  }

  private generatePages(data: ArchitectureData, options: ExportOptions): string {
    let content = '';

    if (options.format === 'executive' || options.format === 'complete') {
      content += this.generateExecutivePage();
    }

    if (options.format === 'technical' || options.format === 'complete') {
      content += this.generateTechnicalPage(data);
    }

    if (options.format === 'usecase' || options.format === 'complete') {
      content += this.generateUseCasePage(data);
    }

    if (options.format === 'prospectus' || options.format === 'complete') {
      content += this.generateProspectusPage();
    }

    return content;
  }

  private generateExecutivePage(): string {
    return `
      <div class="page">
        <div class="header">
          <h1>Bakhmach Business Hub</h1>
          <p>Integrated Platform for Holistic Optimization</p>
        </div>
        <h2>Executive Summary</h2>
        <p>Bakhmach Business Hub is a unified platform integrating code optimization, ML pipelines, production services, personal development, and consciousness research.</p>
        <div class="metrics">
          <div class="metric-box">
            <div>Architecture Layers</div>
            <div class="metric-value">8</div>
          </div>
          <div class="metric-box">
            <div>Core Components</div>
            <div class="metric-value">24+</div>
          </div>
          <div class="metric-box">
            <div>Distribution Channels</div>
            <div class="metric-value">10</div>
          </div>
          <div class="metric-box">
            <div>Use Cases</div>
            <div class="metric-value">10</div>
          </div>
        </div>
      </div>
    `;
  }

  private generateTechnicalPage(data: ArchitectureData): string {
    const nodesTable = data.nodes.map(node => `
      <tr>
        <td>${node.name}</td>
        <td>
          <div class="health-bar">
            <div class="health-fill" style="width: ${node.health}%"></div>
          </div>
        </td>
        <td>${node.health}%</td>
        <td>${node.readiness}%</td>
      </tr>
    `).join('');

    return `
      <div class="page">
        <h2>Technical Architecture</h2>
        <p>Component Health & Readiness Metrics</p>
        <table>
          <thead>
            <tr>
              <th>Component</th>
              <th>Health Status</th>
              <th>Health %</th>
              <th>Readiness %</th>
            </tr>
          </thead>
          <tbody>
            ${nodesTable}
          </tbody>
        </table>
      </div>
    `;
  }

  private generateUseCasePage(data: ArchitectureData): string {
    return `
      <div class="page">
        <h2>Use Cases & Channels</h2>
        <p>10 Primary Use Cases mapped to 10 Distribution Channels</p>
        <h3>Coverage Matrix</h3>
        <p>✓ Web Portal ✓ Mobile PWA ✓ Desktop ✓ XR/VR ✓ REST API ✓ GraphQL ✓ CLI ✓ PDF ✓ WebSocket ✓ Email</p>
      </div>
    `;
  }

  private generateProspectusPage(): string {
    return `
      <div class="page">
        <h2>Investment Prospectus</h2>
        <h3>Market Opportunity: $55B+ TAM</h3>
        <div class="metrics">
          <div class="metric-box">
            <div>Year 1 ARR</div>
            <div class="metric-value">$2.1M</div>
          </div>
          <div class="metric-box">
            <div>Year 2 ARR</div>
            <div class="metric-value">$9.6M</div>
          </div>
          <div class="metric-box">
            <div>Year 3 ARR</div>
            <div class="metric-value">$35M+</div>
          </div>
          <div class="metric-box">
            <div>Target Users</div>
            <div class="metric-value">50K</div>
          </div>
        </div>
      </div>
    `;
  }

  private getPageCount(format: string): number {
    const counts: Record<string, number> = {
      executive: 2,
      technical: 12,
      usecase: 6,
      prospectus: 12,
      complete: 32,
    };
    return counts[format] || 2;
  }

  async close() {
    if (this.browser) {
      await this.browser.close();
    }
  }
}

export default PDFExportService;
