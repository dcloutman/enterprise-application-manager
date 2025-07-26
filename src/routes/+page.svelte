<script lang="ts">
	import { onMount } from 'svelte';

	let tasks: any[] = [];
	let projects: any[] = [];
	let newTaskTitle = '';
	let newProjectName = '';

	const API_BASE = '/api';

	async function fetchTasks() {
		try {
			const response = await fetch(`${API_BASE}/tasks/`);
			if (response.ok) {
				tasks = await response.json();
			}
		} catch (error) {
			console.error('Error fetching tasks:', error);
		}
	}

	async function fetchProjects() {
		try {
			const response = await fetch(`${API_BASE}/projects/`);
			if (response.ok) {
				projects = await response.json();
			}
		} catch (error) {
			console.error('Error fetching projects:', error);
		}
	}

	async function createTask() {
		if (!newTaskTitle.trim()) return;

		try {
			const response = await fetch(`${API_BASE}/tasks/`, {
				method: 'POST',
				headers: {
					'Content-Type': 'application/json',
				},
				body: JSON.stringify({
					title: newTaskTitle,
					description: '',
					completed: false
				})
			});

			if (response.ok) {
				newTaskTitle = '';
				fetchTasks();
			}
		} catch (error) {
			console.error('Error creating task:', error);
		}
	}

	async function createProject() {
		if (!newProjectName.trim()) return;

		try {
			const response = await fetch(`${API_BASE}/projects/`, {
				method: 'POST',
				headers: {
					'Content-Type': 'application/json',
				},
				body: JSON.stringify({
					name: newProjectName,
					description: ''
				})
			});

			if (response.ok) {
				newProjectName = '';
				fetchProjects();
			}
		} catch (error) {
			console.error('Error creating project:', error);
		}
	}

	async function toggleTask(task: any) {
		try {
			const response = await fetch(`${API_BASE}/tasks/${task.id}/`, {
				method: 'PATCH',
				headers: {
					'Content-Type': 'application/json',
				},
				body: JSON.stringify({
					completed: !task.completed
				})
			});

			if (response.ok) {
				fetchTasks();
			}
		} catch (error) {
			console.error('Error updating task:', error);
		}
	}

	onMount(() => {
		fetchTasks();
		fetchProjects();
	});
</script>

<svelte:head>
	<title>App Tracker</title>
	<meta name="description" content="A simple app tracker" />
</svelte:head>

<main>
	<h1>App Tracker</h1>
	
	<section>
		<h2>Tasks</h2>
		<div class="form-group">
			<input 
				bind:value={newTaskTitle} 
				placeholder="Enter new task"
				on:keydown={(e) => e.key === 'Enter' && createTask()}
			/>
			<button onclick={createTask}>Add Task</button>
		</div>
		
		<div class="items">
			{#each tasks as task}
				<div class="item task {task.completed ? 'completed' : ''}">
					<input 
						type="checkbox" 
						checked={task.completed}
						onchange={() => toggleTask(task)}
					/>
					<span class="title">{task.title}</span>
					<span class="date">{new Date(task.created_at).toLocaleDateString()}</span>
				</div>
			{/each}
		</div>
	</section>

	<section>
		<h2>Projects</h2>
		<div class="form-group">
			<input 
				bind:value={newProjectName} 
				placeholder="Enter new project"
				on:keydown={(e) => e.key === 'Enter' && createProject()}
			/>
			<button onclick={createProject}>Add Project</button>
		</div>
		
		<div class="items">
			{#each projects as project}
				<div class="item project">
					<span class="title">{project.name}</span>
					<span class="date">{new Date(project.created_at).toLocaleDateString()}</span>
				</div>
			{/each}
		</div>
	</section>
</main>

<style>
	main {
		max-width: 800px;
		margin: 0 auto;
		padding: 2rem;
		font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
	}

	h1 {
		color: #333;
		text-align: center;
		margin-bottom: 2rem;
	}

	h2 {
		color: #555;
		border-bottom: 2px solid #eee;
		padding-bottom: 0.5rem;
	}

	section {
		margin-bottom: 2rem;
	}

	.form-group {
		display: flex;
		gap: 1rem;
		margin-bottom: 1rem;
	}

	input[type="text"], input:not([type]) {
		flex: 1;
		padding: 0.75rem;
		border: 1px solid #ddd;
		border-radius: 4px;
		font-size: 1rem;
	}

	button {
		padding: 0.75rem 1.5rem;
		background: #007bff;
		color: white;
		border: none;
		border-radius: 4px;
		cursor: pointer;
		font-size: 1rem;
	}

	button:hover {
		background: #0056b3;
	}

	.items {
		display: flex;
		flex-direction: column;
		gap: 0.5rem;
	}

	.item {
		display: flex;
		align-items: center;
		gap: 1rem;
		padding: 1rem;
		border: 1px solid #eee;
		border-radius: 4px;
		background: #f9f9f9;
	}

	.item.completed {
		opacity: 0.6;
	}

	.item.completed .title {
		text-decoration: line-through;
	}

	.title {
		flex: 1;
		font-weight: 600;
	}

	.date {
		color: #666;
		font-size: 0.875rem;
	}

	input[type="checkbox"] {
		width: 1.2rem;
		height: 1.2rem;
	}
</style>
