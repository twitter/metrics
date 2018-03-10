const d3Dsv = require("d3-dsv");
const githubGraphql = require("../github/graphql-api");
const fetch = require("cross-fetch");
const fs = require("fs");
const { promisify } = require("util");
const yargs = require("yargs");

const argv = yargs
	.option('owner', {
		type: 'string',
		default: 'twitter',
	})
	.option('token', {
		type: 'string',
		demandOption: true,
	})
	.option('resource', {
		type: 'string',
		choices: [
			'commits',
			// 'contributions',
			'unique_committers',
			'forks',
			// 'issues/response_time',
			'issues',
			'downloads',
			'pulls/acceptance_rate',
			'pulls',
			'stargazers',
		],
		default: 'pulls',
	})
	.option('group-by', {
		describe: 'only for commits, forks, issues, stargazers',
		type: 'string',
		choices: ['week', 'month', 'year'],
		default: 'month'
	})
	.option('write-csv', {
		describe: 'write out to CSV file',
		type: 'boolean',
		default: true
	})
	.option('write-json', {
		describe: 'write out to JSON file',
		type: 'boolean',
		default: true
	})
	.help()
	.argv;

const { owner, token, resource, writeCsv, writeJson } = argv;
const groupBy = (resource === 'commits' || resource === 'forks' || resource === 'issues' || resource === 'stargazers') ?
	argv.groupBy : null;
const writeCsvPath = `${__dirname}/data/${owner}-${resource}.csv`;
const writeJsonPath = `${__dirname}/data/${owner}-${resource}.json`;
const writeFileAsync = promisify(fs.writeFile);

fetchOrgAllReposTimeseries(owner, token, resource)
	.then(async (AllReposTimeseries) => {
		const writePromises = [];
		if (writeJson) {
			const allReposTimeseriesJson = JSON.stringify(AllReposTimeseries, null, 4);
			writePromises.push(writeFileAsync(writeJsonPath, allReposTimeseriesJson));
		}
		if (writeCsv) {
			const resourceFieldsMapping = {
				commits: ['commits'],
				unique_committers: ['total_unique_committers'],
				forks: ['forks'],
				issues: ['issues'],
				downloads: ['downloads'],
				'pulls/acceptance_rate': ['rate'],
				pulls: ['pull_requests', 'comments'],
				stargazers: ['watchers'],
			};
			const allReposTimeseriesCsv = d3Dsv.csvFormat(AllReposTimeseries,
				["repo", "date", ...resourceFieldsMapping[resource]]);
			writePromises.push(writeFileAsync(writeCsvPath, allReposTimeseriesCsv));
		}
		await Promise.all(writePromises);
	})
	.catch(err => console.error(err));

async function fetchOrgAllReposTimeseries(owner, token, resource) {
	const GHDATA_API_URL = 'http://ghdata.sociallycompute.io/api/unstable';
	const allReposNamesWithOwner = await githubGraphql.fetchOrgAllReposNamesWithOwner(owner, token);
	const allReposTimeseries = [];
	for (const nameWithOwner of allReposNamesWithOwner) {
		const apiUrl = `${GHDATA_API_URL}/${nameWithOwner}/timeseries/${resource}${groupBy ?
			`?group_by=${groupBy}` : ''}`;
		console.log(apiUrl);
		try {
			const res = await fetch(apiUrl);
			if (res.status >= 400) {
				throw new Error(`${apiUrl}
				${res.status}: ${res.statusText}`);
			}
			const timeseries = await res.json();
			timeseries.forEach((resourceAtDate) => resourceAtDate.repo = nameWithOwner);
			allReposTimeseries.push(...timeseries);
		} catch (err) {
			console.error(err);
		}
	}
	return allReposTimeseries;
}