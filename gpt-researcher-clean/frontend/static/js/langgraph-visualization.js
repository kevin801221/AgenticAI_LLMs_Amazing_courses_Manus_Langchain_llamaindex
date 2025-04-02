// 這個文件將被添加到前端以加載和顯示 LangGraph 視覺化
// 使用 d3.js 來渲染研究流程圖

// 引入 d3.js (在 HTML 文件中添加: <script src="https://d3js.org/d3.v7.min.js"></script>)

class ResearchFlowVisualizer {
    constructor(containerId, options = {}) {
        this.containerId = containerId;
        this.options = {
            width: options.width || 600,
            height: options.height || 400,
            nodeRadius: options.nodeRadius || 20,
            colors: options.colors || {
                search: '#4CAF50',      // 綠色
                analyze: '#2196F3',     // 藍色
                summarize: '#FF9800',   // 橙色
                report: '#E91E63',      // 粉紅色
                completed: '#9C27B0',   // 紫色
                inactive: '#757575'     // 灰色
            }
        };
        
        this.svg = null;
        this.simulation = null;
        this.nodes = [];
        this.links = [];
    }
    
    initialize() {
        const container = d3.select(`#${this.containerId}`);
        container.selectAll("*").remove();
        
        this.svg = container.append('svg')
            .attr('width', this.options.width)
            .attr('height', this.options.height)
            .attr('viewBox', [0, 0, this.options.width, this.options.height])
            .attr('style', 'max-width: 100%; height: auto;');
            
        // 添加箭頭標記定義
        this.svg.append('defs')
            .append('marker')
            .attr('id', 'arrowhead')
            .attr('viewBox', '0 -5 10 10')
            .attr('refX', 20)
            .attr('refY', 0)
            .attr('orient', 'auto')
            .attr('markerWidth', 6)
            .attr('markerHeight', 6)
            .append('path')
            .attr('d', 'M0,-5L10,0L0,5')
            .attr('fill', '#999');
    }
    
    // 使用實際的 langgraph 數據更新可視化
    updateFromLanggraph(data) {
        if (!this.svg) this.initialize();
        
        // 將 langgraph 格式轉換為 d3 可視化所需的格式
        this.nodes = this._extractNodes(data);
        this.links = this._extractLinks(data);
        
        this._renderGraph();
    }
    
    // 從 langgraph 數據中提取節點
    _extractNodes(data) {
        const nodes = [];
        
        // 處理研究階段節點
        if (data.nodes) {
            data.nodes.forEach((node, index) => {
                nodes.push({
                    id: node.id || `node-${index}`,
                    name: node.name || `步驟 ${index + 1}`,
                    type: node.type || 'default',
                    status: node.status || 'inactive',
                    description: node.description || '',
                    x: this.options.width / 2 + (Math.random() - 0.5) * 100,
                    y: this.options.height / 2 + (Math.random() - 0.5) * 100
                });
            });
        }
        
        return nodes;
    }
    
    // 從 langgraph 數據中提取連接
    _extractLinks(data) {
        const links = [];
        
        // 處理研究流程連接
        if (data.edges) {
            data.edges.forEach((edge, index) => {
                links.push({
                    id: `link-${index}`,
                    source: edge.source,
                    target: edge.target,
                    label: edge.label || '',
                    completed: edge.completed || false
                });
            });
        }
        
        return links;
    }
    
    // 渲染圖形
    _renderGraph() {
        // 清除之前的圖形
        this.svg.selectAll("*").remove();
        
        // 重新添加箭頭標記定義
        this.svg.append('defs')
            .append('marker')
            .attr('id', 'arrowhead')
            .attr('viewBox', '0 -5 10 10')
            .attr('refX', 20)
            .attr('refY', 0)
            .attr('orient', 'auto')
            .attr('markerWidth', 6)
            .attr('markerHeight', 6)
            .append('path')
            .attr('d', 'M0,-5L10,0L0,5')
            .attr('fill', '#999');
            
        // 創建力導向模擬
        this.simulation = d3.forceSimulation(this.nodes)
            .force('link', d3.forceLink(this.links).id(d => d.id).distance(100))
            .force('charge', d3.forceManyBody().strength(-300))
            .force('center', d3.forceCenter(this.options.width / 2, this.options.height / 2))
            .force('collision', d3.forceCollide().radius(this.options.nodeRadius * 1.5));
            
        // 繪製連接線
        const link = this.svg.append('g')
            .attr('class', 'links')
            .selectAll('line')
            .data(this.links)
            .join('line')
            .attr('stroke-width', d => d.completed ? 3 : 1.5)
            .attr('stroke', d => d.completed ? '#4CAF50' : '#999')
            .attr('marker-end', 'url(#arrowhead)');
            
        // 添加連接標籤
        const linkLabels = this.svg.append('g')
            .attr('class', 'link-labels')
            .selectAll('text')
            .data(this.links)
            .join('text')
            .text(d => d.label)
            .attr('fill', '#555')
            .attr('font-size', '10px')
            .attr('text-anchor', 'middle');
            
        // 繪製節點
        const nodeGroup = this.svg.append('g')
            .attr('class', 'nodes')
            .selectAll('g')
            .data(this.nodes)
            .join('g')
            .call(this._setupDrag(this.simulation));
            
        // 添加節點圓形
        nodeGroup.append('circle')
            .attr('r', this.options.nodeRadius)
            .attr('fill', d => this._getNodeColor(d))
            .attr('stroke', '#fff')
            .attr('stroke-width', 2);
            
        // 添加節點標籤
        nodeGroup.append('text')
            .text(d => d.name)
            .attr('text-anchor', 'middle')
            .attr('dy', this.options.nodeRadius + 15)
            .attr('font-size', '12px')
            .attr('fill', '#333');
            
        // 添加滑鼠懸停效果
        nodeGroup
            .on('mouseover', (event, d) => {
                const tooltip = d3.select('body').append('div')
                    .attr('class', 'tooltip')
                    .style('position', 'absolute')
                    .style('background', 'rgba(0,0,0,0.7)')
                    .style('color', 'white')
                    .style('padding', '5px 10px')
                    .style('border-radius', '5px')
                    .style('pointer-events', 'none')
                    .style('z-index', 1000)
                    .style('top', (event.pageY - 10) + 'px')
                    .style('left', (event.pageX + 10) + 'px')
                    .html(`<strong>${d.name}</strong><br>${d.description}`);
            })
            .on('mouseout', () => {
                d3.selectAll('.tooltip').remove();
            });
            
        // 更新模擬
        this.simulation.on('tick', () => {
            link
                .attr('x1', d => d.source.x)
                .attr('y1', d => d.source.y)
                .attr('x2', d => d.target.x)
                .attr('y2', d => d.target.y);
                
            linkLabels
                .attr('x', d => (d.source.x + d.target.x) / 2)
                .attr('y', d => (d.source.y + d.target.y) / 2);
                
            nodeGroup.attr('transform', d => `translate(${d.x},${d.y})`);
        });
    }
    
    // 設置拖拽行為
    _setupDrag(simulation) {
        return d3.drag()
            .on('start', (event, d) => {
                if (!event.active) simulation.alphaTarget(0.3).restart();
                d.fx = d.x;
                d.fy = d.y;
            })
            .on('drag', (event, d) => {
                d.fx = event.x;
                d.fy = event.y;
            })
            .on('end', (event, d) => {
                if (!event.active) simulation.alphaTarget(0);
                d.fx = null;
                d.fy = null;
            });
    }
    
    // 獲取節點顏色
    _getNodeColor(node) {
        if (node.status === 'completed') return this.options.colors.completed;
        switch (node.type) {
            case 'search': return this.options.colors.search;
            case 'analyze': return this.options.colors.analyze;
            case 'summarize': return this.options.colors.summarize;
            case 'report': return this.options.colors.report;
            default: return this.options.colors.inactive;
        }
    }
    
    // 加載示例數據 (在實際整合前用於測試)
    loadExampleData() {
        const exampleData = {
            nodes: [
                { id: 'start', name: '開始', type: 'search', status: 'completed', description: '開始研究流程' },
                { id: 'search', name: '網絡搜尋', type: 'search', status: 'completed', description: '從PubMed、ArXiv等搜尋相關文獻' },
                { id: 'analyze', name: '數據分析', type: 'analyze', status: 'active', description: '分析收集的真菌數據' },
                { id: 'extract', name: '信息提取', type: 'analyze', status: 'inactive', description: '從文獻中提取關鍵信息' },
                { id: 'summarize', name: '研究總結', type: 'summarize', status: 'inactive', description: '總結研究發現' },
                { id: 'report', name: '報告生成', type: 'report', status: 'inactive', description: '生成最終研究報告' }
            ],
            edges: [
                { source: 'start', target: 'search', label: '初始化', completed: true },
                { source: 'search', target: 'analyze', label: '提供數據', completed: true },
                { source: 'analyze', target: 'extract', label: '深入分析' },
                { source: 'extract', target: 'summarize', label: '整合發現' },
                { source: 'summarize', target: 'report', label: '編纂報告' }
            ]
        };
        
        this.updateFromLanggraph(exampleData);
    }
}