const { fetchOrgAllReposTotalCounts } = require("../github/graphql-api");
const { promisify } = require("util");
const fs = require("fs");
const writeFileAsync = promisify(fs.writeFile);
const yargs = require("yargs");

const argv = yargs
	.option('orgs', {
		type: 'array',
		default: [
			"twitter",
			"twitter-forks",
			"twitter-archive",
			"twitterdev",
			"twitter-university",
			"finagle",
			"vine",
			"pantsbuild",
			"gnip",
			"bountylabs",
			// "TwitterGlobalCreative", // has no repositories
			"flightjs",
			"tweetdeck",
			"mopub",
			"snappytv"
		],
		describe: "Set of Github organizations to configure projects.json for GrimoireLab"
	})
	.option('token', {
		type: 'string',
		demandOption: true,
		describe: "Github API Token to find all repositories for each Github organization"
	})
	.option('repo-project', {
		type: 'boolean',
		default: true,
		describe: "Treat each Github repository as a 'project' for GrimoireLab"
	})
	.option('org-project', {
		type: 'boolean',
		default: false,
		describe: "Treat each Github organization as a 'project' for GrimoireLab"
	})
	.help()
	.argv;

const { orgs, token, repoProject, orgProject } = argv;
const flattenReposTotalCounts = true;

orgs.reduce(async (projectsDictPromise, org) => {
	const promises = [fetchOrgAllReposTotalCounts(org, token, flattenReposTotalCounts), projectsDictPromise];
	const [reposTotalCounts, projectsDict] = await Promise.all(promises);
	const repoNamesWithOwner = reposTotalCounts.map(repoTotalCount => repoTotalCount.nameWithOwner);

	if (orgProject) { // each Github org as a 'project'
		const reposGitLinks = repoNamesWithOwner.map(gitLinkFromRepo);
		projectsDict[org] = { git: reposGitLinks, github: reposGitLinks };
	}

	if (repoProject) { // each Github repo as a 'project'
		repoNamesWithOwner.forEach(repoNameWithOwner => {
			const repoGitLink = gitLinkFromRepo(repoNameWithOwner);
			projectsDict[repoNameWithOwner] = { git: [repoGitLink], github: [repoGitLink] };
		});
	}
	return projectsDict;
}, Promise.resolve({}))
	.then(projectsDict => writeFileAsync('projects.json', JSON.stringify(projectsDict, null, 4), 'utf8'))
	.then(() => console.log('Wrote ./projects.json'))
	.catch(err => console.log(err));

function gitLinkFromRepo(nameWithOwner) {
	return `https://github.com/${nameWithOwner}.git`
}