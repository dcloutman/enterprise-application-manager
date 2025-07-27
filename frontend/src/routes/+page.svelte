<svelte:head>
	<title>Setup Complete</title>
	<meta name="description" content="Django + SvelteKit Docker setup" />
</svelte:head>

<main>
	<h1>🎉 Setup Complete!</h1>
	
	<div class="status">
		<h2>Your Django + SvelteKit application is running:</h2>
		<ul>
			<li>✅ <strong>SvelteKit Frontend</strong>: Running with hot-reload on port 3000</li>
			<li>✅ <strong>Django Backend</strong>: Running with Gunicorn on port 8000</li>
			<li>✅ <strong>MySQL Database</strong>: Running on port 3306</li>
			<li>✅ <strong>Nginx Proxy</strong>: Routing traffic on port 80</li>
			<li>✅ <strong>Docker Swarm</strong>: Orchestrating with 2 app replicas</li>
		</ul>
	</div>

	<div class="links">
		<h3>Access Points:</h3>
		<ul>
			<li><a href="/admin/">Django Admin</a> (admin/admin123)</li>
			<li><a href="/api/">Django REST API</a></li>
		</ul>
	</div>

	<div class="tech-stack">
		<h3>Tech Stack:</h3>
		<ul>
			<li><strong>Frontend</strong>: SvelteKit with TypeScript</li>
			<li><strong>Backend</strong>: Django 4.2+ with Django REST Framework</li>
			<li><strong>Database</strong>: MySQL 8.4</li>
			<li><strong>Web Server</strong>: Nginx</li>
			<li><strong>Deployment</strong>: Docker Swarm with Oracle Linux 8</li>
			<li><strong>Runtime</strong>: Python 3.12, Node.js 22 LTS</li>
		</ul>
	</div>
</main>

<style>
	main {
		max-width: 800px;
		margin: 0 auto;
		padding: 2rem;
		font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
		line-height: 1.6;
	}

	h1 {
		color: #2d5a27;
		text-align: center;
		margin-bottom: 2rem;
		font-size: 2.5rem;
	}

	h2 {
		color: #333;
		border-bottom: 2px solid #eee;
		padding-bottom: 0.5rem;
		margin-top: 2rem;
	}

	h3 {
		color: #555;
		margin-top: 1.5rem;
	}

	.status, .links, .tech-stack {
		margin-bottom: 2rem;
		padding: 1.5rem;
		background: #f8f9fa;
		border-radius: 8px;
		border-left: 4px solid #28a745;
	}

	ul {
		margin: 1rem 0;
	}

	li {
		margin: 0.5rem 0;
	}

	a {
		color: #007bff;
		text-decoration: none;
	}

	a:hover {
		text-decoration: underline;
	}

	strong {
		color: #333;
	}
</style>
