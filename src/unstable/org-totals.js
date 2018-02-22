const fs = require("fs");
const path = require("path");
const { promisify } = require("util");
const readFileAsync = promisify(fs.readFile);
const writeFileAsync = promisify(fs.writeFile);
const { fetchOrgAllReposTotalCounts } = require("../github/graphql-api");
const yargs = require("yargs");

// TODO: work in progress below: much reworking/refactoring required

const { argv } = yargs
    .option('owner', {
        default: 'twitter',
        type: 'string',
    })
    .option('token', {
        demandOption: true,
        type: 'string'
    })
    .option('cache', {
        type: 'boolean',
        default: false,
    });

const { owner, token, cache: fromRepoTotals } = argv;

// saveOrgTotals(owner, fromRepoTotals).catch(err => console.log(err));
// saveReposDiff(owner, token).catch((err) => console.log(err));
saveOrgDiff(owner, token).catch((err) => console.log(err));

async function saveOrgDiff(owner, token) {
    const orgTotalsPath = path.join(__dirname,'..','..','docs','data',owner,'org-totals.json');
    const oldOrgTotals = JSON.parse(fs.readFileSync(orgTotalsPath, 'utf8'));
    const newOrgTotals = await orgTotalsFromFetchRepoTotals(owner, token);
    const orgTotalsDiff = diffObject(oldOrgTotals, newOrgTotals);

    const newOrgTotalsPath = path.join(__dirname,'..','..','docs','data',owner,'new-org-totals.json');
    const orgTotalsDiffPath = path.join(__dirname,'..','..','docs','data',owner,'org-totals-diff.json');
    fs.writeFileSync(newOrgTotalsPath, JSON.stringify(newOrgTotals, null, 4), 'utf8');
    fs.writeFileSync(orgTotalsDiffPath, JSON.stringify(orgTotalsDiff, null, 4), 'utf8');
}

async function saveReposDiff(owner, token) {
    const oldReposTotalsPath = path.join(__dirname,'..','..','docs','data',owner,'repos-totals.json');
    const oldReposTotals = JSON.parse(fs.readFileSync(oldReposTotalsPath, 'utf8'));
    const flattenRepoCounts = true;
    const newReposTotals = await fetchOrgAllReposTotalCounts(owner, token, flattenRepoCounts);
    const reposTotalsDiff = diffObjects(oldReposTotals, newReposTotals, 'nameWithOwner');

    const newReposTotalsPath = path.join(__dirname,'..','..','docs','data',owner,'new-repos-totals.json');
    const reposTotalsDiffPath = path.join(__dirname,'..','..','docs','data',owner,'repos-totals-diff.json');
    fs.writeFileSync(reposTotalsDiffPath, JSON.stringify(reposTotalsDiff, null, 4), 'utf8');
    fs.writeFileSync(newReposTotalsPath, JSON.stringify(newReposTotals, null, 4), 'utf8');
}

async function saveOrgTotals(owner, fromRepoTotals) {
    const reposTotalsPath = path.join(__dirname,'..','..','docs','data',owner,'repos-totals.json');
    const orgTotalsPath = path.join(__dirname,'..','..','docs','data',owner,'org-totals.json');

    let reposTotals;
    if (fromRepoTotals) {
        reposTotals = JSON.parse(await readFileAsync(reposTotalsPath, 'utf8'));
        console.log(`read repo totals from ${reposTotalsPath}`);
    } else {
        const flattenRepoTotalCounts = true;
        reposTotals = await fetchOrgAllReposTotalCounts(owner, token, flattenRepoTotalCounts);
        await writeFileAsync(reposTotalsPath, JSON.stringify(reposTotals), 'utf8');
        console.log(`wrote repo totals to ${reposTotalsPath}`);
    }
    const orgTotals = orgTotalsFromReposTotals(reposTotals);
    await writeFileAsync(orgTotalsPath, JSON.stringify(orgTotals), 'utf8');
    console.log(`wrote org totals to ${orgTotalsPath}`);
}

function orgTotalsFromReposTotals(reposTotals) {
    const orgTotals = {};
    for (const repoTotals of reposTotals) {
        for (const [key, value] of Object.entries(repoTotals)) {
            if (typeof value === 'number') {
                orgTotals[key] = orgTotals[key] ? orgTotals[key] + value : value;
            }
        }
    }
    orgTotals.repositories = reposTotals.length;
    return orgTotals;
}

async function orgTotalsFromFetchRepoTotals(owner, token) {
    const flattenRepoTotalCounts = true;
    const reposTotals = await fetchOrgAllReposTotalCounts(owner, token, flattenRepoTotalCounts);
    return orgTotalsFromReposTotals(reposTotals);
}

function diffObject(oldObject, newObject) { // for org
    const diffs = {};
    for (const [currKey, currValue] of Object.entries(newObject)) {
        if (typeof(currValue) === 'number') {
            const prevValue = oldObject[currKey];
            const valueDiff = currValue - prevValue;
            diffs[currKey] = valueDiff;
        } else {
            diffs[currKey] = currValue;
        }
    }
    return diffs;
}

function diffObjects(oldObjectsList, newObjectsList, keyName) { // for repos
    const allDiffs = [];
    const oldObjectsMap = new Map();
    for (const oldObject of oldObjectsList) {
        oldObjectsMap.set(oldObject[keyName], oldObject);
    }
    for (const newObject of newObjectsList) {
        const keyValue = newObject[keyName];
        const oldObject = oldObjectsMap.get(keyValue);
        if (oldObject == undefined) {
            console.error(`New repository found: ${keyValue}`); // TODO: handle deleted repositories?
            allDiffs.push(newObject);
        } else {
            const objectDiff = diffObject(oldObject, newObject);
            allDiffs.push(objectDiff);
        }
    }
    return allDiffs;
}
