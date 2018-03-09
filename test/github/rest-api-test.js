const githubApi = require('../../src/github/rest-api');

githubApi.fetchRepoResourceList('twitter', 'typeahead.js', 'pulls', '336331c85fc6aeedc6e2507aa183276dd1376f94', 200, true)
	.then(repoResourceList => console.log(repoResourceList.length))
	.catch(err => console.log(err));