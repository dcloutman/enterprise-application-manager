<svelte:head>
	<title>Government IT Asset Management</title>
	<meta name="description" content="Enterprise Application Tracker" />
</svelte:head>

<script>
	import { onMount } from 'svelte';
	
	let dashboardStats = null;
	let applications = [];
	let servers = [];
	let languages = [];
	let datastores = [];
	let loading = true;
	let error = null;

	async function fetchData() {
		try {
			// Fetch dashboard statistics
			const statsResponse = await fetch('/api/applications/dashboard_stats/');
			if (statsResponse.ok) {
				dashboardStats = await statsResponse.json();
			}

			// Fetch applications
			const appsResponse = await fetch('/api/applications/?limit=10');
			if (appsResponse.ok) {
				const appsData = await appsResponse.json();
				applications = appsData.results || [];
			}

			// Fetch servers
			const serversResponse = await fetch('/api/servers/?limit=10');
			if (serversResponse.ok) {
				const serversData = await serversResponse.json();
				servers = serversData.results || [];
			}

			// Fetch languages
			const languagesResponse = await fetch('/api/languages/');
			if (languagesResponse.ok) {
				const languagesData = await languagesResponse.json();
				languages = languagesData.results || [];
			}

			// Fetch datastores
			const datastoresResponse = await fetch('/api/datastores/');
			if (datastoresResponse.ok) {
				const datastoresData = await datastoresResponse.json();
				datastores = datastoresData.results || [];
			}

			loading = false;
		} catch (err) {
			error = err.message;
			loading = false;
		}
	}

	onMount(fetchData);
</script>

<main>
	<header>
		<h1>🏛️ Government IT Asset Management</h1>
		<p>Enterprise Application Tracker - Comprehensive IT Infrastructure Management</p>
	</header>

	{#if loading}
		<div class="loading">
			<div class="spinner"></div>
			<p>Loading dashboard data...</p>
		</div>
	{:else if error}
		<div class="error">
			<h2>⚠️ Error Loading Data</h2>
			<p>{error}</p>
			<button on:click={fetchData}>Retry</button>
		</div>
	{:else}
		<!-- Dashboard Statistics -->
		{#if dashboardStats}
			<section class="dashboard-stats">
				<h2>📊 Dashboard Overview</h2>
				<div class="stats-grid">
					<div class="stat-card">
						<h3>{dashboardStats.total_applications}</h3>
						<p>Total Applications</p>
					</div>
					<div class="stat-card">
						<h3>{dashboardStats.active_applications}</h3>
						<p>Active Applications</p>
					</div>
					<div class="stat-card">
						<h3>{servers.length}</h3>
						<p>Server Environments</p>
					</div>
					<div class="stat-card">
						<h3>{languages.length}</h3>
						<p>Programming Languages</p>
					</div>
				</div>
				
				{#if dashboardStats.by_lifecycle_stage?.length > 0}
					<div class="chart-section">
						<h3>Applications by Lifecycle Stage</h3>
						<div class="stage-chart">
							{#each dashboardStats.by_lifecycle_stage as stage}
								<div class="stage-item" title="{stage.count} applications in {stage.lifecycle_stage}">
									<span class="stage-label">{stage.lifecycle_stage}</span>
									<span class="stage-count">{stage.count}</span>
								</div>
							{/each}
						</div>
					</div>
				{/if}
			</section>
		{/if}

		<!-- Applications Section -->
		<section class="applications">
			<h2>🖥️ Recent Applications</h2>
			{#if applications.length > 0}
				<div class="app-grid">
					{#each applications as app}
						<div class="app-card">
							<h3>{app.name}</h3>
							<p class="app-description">{app.description || 'No description available'}</p>
							<div class="app-details">
								<span class="badge badge-{app.lifecycle_stage}">{app.lifecycle_stage}</span>
								<span class="badge badge-{app.criticality}">{app.criticality}</span>
							</div>
							<div class="app-meta">
								<p><strong>Owner:</strong> {app.business_owner || 'Unassigned'}</p>
								<p><strong>Server:</strong> {app.primary_server_hostname || 'Not deployed'}</p>
							</div>
						</div>
					{/each}
				</div>
				<div class="view-all">
					<a href="/api/applications/" target="_blank">View All Applications →</a>
				</div>
			{:else}
				<p>No applications found. <a href="/admin/">Add some applications</a> to get started.</p>
			{/if}
		</section>

		<!-- Servers Section -->
		<section class="servers">
			<h2>🖥️ Server Environments</h2>
			{#if servers.length > 0}
				<div class="server-grid">
					{#each servers as server}
						<div class="server-card">
							<h3>{server.hostname}</h3>
							<p class="server-name">{server.name}</p>
							<div class="server-details">
								<span class="badge badge-{server.environment_type}">{server.environment_type}</span>
								<span class="server-ip">{server.ip_address}</span>
							</div>
							<div class="server-specs">
								<p><strong>OS:</strong> {server.operating_system} {server.os_version || ''}</p>
								{#if server.cpu_cores}
									<p><strong>Resources:</strong> {server.cpu_cores} cores, {server.memory_gb}GB RAM</p>
								{/if}
							</div>
						</div>
					{/each}
				</div>
				<div class="view-all">
					<a href="/api/servers/" target="_blank">View All Servers →</a>
				</div>
			{:else}
				<p>No servers found.</p>
			{/if}
		</section>

		<!-- Technology Stack -->
		<section class="tech-stack">
			<div class="tech-section">
				<h3>📚 Programming Languages</h3>
				{#if languages.length > 0}
					<div class="tech-list">
						{#each languages as lang}
							<span class="tech-badge">{lang.name}</span>
						{/each}
					</div>
				{:else}
					<p>No languages configured.</p>
				{/if}
			</div>
			
			<div class="tech-section">
				<h3>🗄️ Data Stores</h3>
				{#if datastores.length > 0}
					<div class="tech-list">
						{#each datastores as ds}
							<span class="tech-badge">{ds.name} ({ds.datastore_type})</span>
						{/each}
					</div>
				{:else}
					<p>No datastores configured.</p>
				{/if}
			</div>
		</section>

		<!-- Quick Links -->
		<section class="quick-links">
			<h2>🔗 Quick Links</h2>
			<div class="links-grid">
				<a href="/admin/" class="quick-link" target="_blank">
					<h3>🛠️ Admin Panel</h3>
					<p>Manage applications, servers, and infrastructure</p>
				</a>
				<a href="/api/" class="quick-link" target="_blank">
					<h3>🔌 API Browser</h3>
					<p>Explore REST API endpoints and data</p>
				</a>
				<a href="http://localhost:3000" class="quick-link" target="_blank">
					<h3>🔧 Development Server</h3>
					<p>Frontend development with hot-reload</p>
				</a>
			</div>
		</section>
	{/if}
</main>

<style>
	:global(body) {
		margin: 0;
		padding: 0;
		font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', 'Oxygen', 'Ubuntu', 'Cantarell', 'Open Sans', 'Helvetica Neue', sans-serif;
		background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
		min-height: 100vh;
		color: #333;
	}

	main {
		max-width: 1200px;
		margin: 0 auto;
		padding: 2rem;
	}

	header {
		text-align: center;
		margin-bottom: 3rem;
		color: white;
	}

	header h1 {
		font-size: 3rem;
		margin-bottom: 0.5rem;
		text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
	}

	header p {
		font-size: 1.2rem;
		opacity: 0.9;
	}

	section {
		background: white;
		border-radius: 12px;
		padding: 2rem;
		margin-bottom: 2rem;
		box-shadow: 0 4px 6px rgba(0,0,0,0.1);
	}

	section h2 {
		color: #4a5568;
		margin-bottom: 1rem;
		border-bottom: 2px solid #e2e8f0;
		padding-bottom: 0.5rem;
	}

	.loading {
		text-align: center;
		padding: 3rem;
		color: white;
	}

	.spinner {
		border: 4px solid rgba(255,255,255,0.3);
		border-top: 4px solid white;
		border-radius: 50%;
		width: 40px;
		height: 40px;
		animation: spin 1s linear infinite;
		margin: 0 auto 1rem;
	}

	@keyframes spin {
		0% { transform: rotate(0deg); }
		100% { transform: rotate(360deg); }
	}

	.error {
		background: #fed7d7;
		border: 1px solid #fc8181;
		border-radius: 8px;
		padding: 2rem;
		color: #742a2a;
		text-align: center;
	}

	.error button {
		background: #e53e3e;
		color: white;
		border: none;
		padding: 0.5rem 1rem;
		border-radius: 6px;
		cursor: pointer;
		margin-top: 1rem;
	}

	.stats-grid {
		display: grid;
		grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
		gap: 1rem;
		margin-bottom: 2rem;
	}

	.stat-card {
		background: #f7fafc;
		border-radius: 8px;
		padding: 1.5rem;
		text-align: center;
		border-left: 4px solid #4299e1;
	}

	.stat-card h3 {
		font-size: 2.5rem;
		color: #2d3748;
		margin: 0 0 0.5rem 0;
	}

	.stat-card p {
		color: #718096;
		margin: 0;
		font-weight: 500;
	}

	.stage-chart {
		display: flex;
		flex-wrap: wrap;
		gap: 1rem;
	}

	.stage-item {
		background: #edf2f7;
		border-radius: 8px;
		padding: 1rem;
		display: flex;
		flex-direction: column;
		align-items: center;
		min-width: 120px;
	}

	.stage-label {
		font-weight: 600;
		color: #4a5568;
		text-transform: capitalize;
	}

	.stage-count {
		font-size: 1.5rem;
		font-weight: bold;
		color: #2d3748;
	}

	.app-grid, .server-grid {
		display: grid;
		grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
		gap: 1.5rem;
	}

	.app-card, .server-card {
		background: #f7fafc;
		border-radius: 8px;
		padding: 1.5rem;
		border-left: 4px solid #38b2ac;
		transition: transform 0.2s, box-shadow 0.2s;
	}

	.app-card:hover, .server-card:hover {
		transform: translateY(-2px);
		box-shadow: 0 4px 12px rgba(0,0,0,0.15);
	}

	.app-card h3, .server-card h3 {
		color: #2d3748;
		margin: 0 0 0.5rem 0;
		font-size: 1.2rem;
	}

	.app-description, .server-name {
		color: #718096;
		margin-bottom: 1rem;
		font-size: 0.9rem;
	}

	.app-details, .server-details {
		display: flex;
		gap: 0.5rem;
		margin-bottom: 1rem;
		flex-wrap: wrap;
	}

	.badge {
		padding: 0.25rem 0.5rem;
		border-radius: 4px;
		font-size: 0.75rem;
		font-weight: 600;
		text-transform: uppercase;
	}

	.badge-production { background: #c6f6d5; color: #22543d; }
	.badge-development { background: #feebc8; color: #c05621; }
	.badge-testing { background: #bee3f8; color: #2c5282; }
	.badge-retired { background: #fed7d7; color: #742a2a; }
	.badge-high { background: #fed7d7; color: #742a2a; }
	.badge-medium { background: #feebc8; color: #c05621; }
	.badge-low { background: #c6f6d5; color: #22543d; }
	.badge-physical { background: #e6fffa; color: #234e52; }
	.badge-virtual { background: #ebf4ff; color: #2a4365; }
	.badge-container { background: #f0fff4; color: #22543d; }
	.badge-cloud { background: #fef5e7; color: #744210; }

	.server-ip {
		font-family: 'Monaco', 'Menlo', monospace;
		background: #edf2f7;
		padding: 0.25rem 0.5rem;
		border-radius: 4px;
		font-size: 0.8rem;
	}

	.app-meta, .server-specs {
		font-size: 0.85rem;
		color: #4a5568;
	}

	.app-meta p, .server-specs p {
		margin: 0.25rem 0;
	}

	.tech-stack {
		display: grid;
		grid-template-columns: 1fr 1fr;
		gap: 2rem;
	}

	.tech-section h3 {
		color: #4a5568;
		margin-bottom: 1rem;
	}

	.tech-list {
		display: flex;
		flex-wrap: wrap;
		gap: 0.5rem;
	}

	.tech-badge {
		background: #edf2f7;
		color: #4a5568;
		padding: 0.5rem 1rem;
		border-radius: 20px;
		font-size: 0.85rem;
		font-weight: 500;
	}

	.links-grid {
		display: grid;
		grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
		gap: 1rem;
	}

	.quick-link {
		display: block;
		background: #f7fafc;
		border-radius: 8px;
		padding: 1.5rem;
		text-decoration: none;
		color: inherit;
		border-left: 4px solid #805ad5;
		transition: transform 0.2s, box-shadow 0.2s;
	}

	.quick-link:hover {
		transform: translateY(-2px);
		box-shadow: 0 4px 12px rgba(0,0,0,0.15);
	}

	.quick-link h3 {
		color: #553c9a;
		margin: 0 0 0.5rem 0;
	}

	.quick-link p {
		color: #718096;
		margin: 0;
		font-size: 0.9rem;
	}

	.view-all {
		text-align: center;
		margin-top: 1.5rem;
	}

	.view-all a {
		color: #667eea;
		text-decoration: none;
		font-weight: 600;
	}

	.view-all a:hover {
		text-decoration: underline;
	}

	@media (max-width: 768px) {
		main {
			padding: 1rem;
		}
		
		header h1 {
			font-size: 2rem;
		}
		
		.tech-stack {
			grid-template-columns: 1fr;
		}
		
		.stats-grid {
			grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
		}
	}
</style>
