const { fetchOrgAllReposTotalCounts } = require("../github/graphql-api");
const { promisify } = require("util");
const fs = require("fs");
const writeFileAsync = promisify(fs.writeFile);
const yargs = require("yargs");

const { owners, token } = yargs
	.option('owners', {
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
		type: 'array',
	})
	.option('token', {
		demandOption: true,
		type: 'string'
	})
	.help()
	.argv;

const flattenReposTotalCounts = true;
owners.reduce(async (projectsDictPromise, owner) => {
	const promises = [fetchOrgAllReposTotalCounts(owner, token, flattenReposTotalCounts), projectsDictPromise];
	const [reposTotalCounts, projectsDict] = await Promise.all(promises);
	const reposGitLinks = reposTotalCounts.map(repoTotalCount => `https://github.com/${repoTotalCount.nameWithOwner}.git`);
	projectsDict[owner] = { git: reposGitLinks, github: reposGitLinks };
	return projectsDict;
}, Promise.resolve({}))
	.then(projectsDict => writeFileAsync('projects.json', JSON.stringify(projectsDict, null, 4), 'utf8'))
	.then(() => console.log('Wrote ./projects.json'))
	.catch(err => console.log(err));