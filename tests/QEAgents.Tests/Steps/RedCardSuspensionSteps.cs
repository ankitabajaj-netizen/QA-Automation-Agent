using System.Diagnostics;
using BettingPlatform;
using NUnit.Framework;
using QEAgents.Tests.Support;
using Reqnroll;

namespace QEAgents.Tests.Steps;

/// <summary>
/// Step vocabulary bound here is intentionally small and fixed - the Generator agent is
/// constrained (via prompt + an output allow-list check) to only ever emit these exact
/// phrasings. See plan.md, "Test Generation" and "Safety".
/// </summary>
[Binding]
public class RedCardSuspensionSteps
{
    private readonly BettingContext _context;

    public RedCardSuspensionSteps(BettingContext context)
    {
        _context = context;
    }

    [Given(@"a match ""(.*)"" is in progress")]
    public void GivenAMatchIsInProgress(string matchName)
    {
        _context.MatchId = matchName;
    }

    [Given(@"the following players are in the match:")]
    public void GivenTheFollowingPlayersAreInTheMatch(Table table)
    {
        foreach (var row in table.Rows)
        {
            var player = new Player
            {
                PlayerId = row["playerId"],
                Name = row["playerName"],
                Team = row["team"]
            };
            _context.Players[player.PlayerId] = player;
        }
    }

    [Given(@"the following betting markets are open for the match:")]
    public void GivenTheFollowingBettingMarketsAreOpenForTheMatch(Table table)
    {
        foreach (var row in table.Rows)
        {
            var eligible = row["eligiblePlayerIds"];
            var market = new Market
            {
                MarketId = row["marketId"],
                MarketType = row["marketType"],
                EligiblePlayerIds = string.IsNullOrWhiteSpace(eligible)
                    ? new List<string>()
                    : eligible.Split(',', StringSplitOptions.TrimEntries | StringSplitOptions.RemoveEmptyEntries).ToList()
            };
            _context.Markets[market.MarketId] = market;
        }

        _context.InitializeService();
    }

    [When(@"player ""(.*)"" receives a red card")]
    public void WhenPlayerReceivesARedCard(string playerName)
    {
        _context.FireRedCard(_context.PlayerIdByName(playerName));
    }

    [When(@"player ""(.*)"" receives a red card again")]
    public void WhenPlayerReceivesARedCardAgain(string playerName)
    {
        _context.FireRedCard(_context.PlayerIdByName(playerName));
    }

    [When(@"player ""(.*)"" receives a second yellow card resulting in a red card")]
    public void WhenPlayerReceivesASecondYellowCardResultingInARedCard(string playerName)
    {
        _context.FireRedCard(_context.PlayerIdByName(playerName));
    }

    [Then(@"market ""(.*)"" should be ""(.*)""")]
    public async Task ThenMarketShouldBe(string marketId, string expectedStatus)
    {
        var expected = Enum.Parse<MarketStatus>(expectedStatus, ignoreCase: true);
        var market = _context.Markets[marketId];

        if (expected == MarketStatus.Suspended)
        {
            // Suspension is applied asynchronously by the platform; poll generously so this
            // assertion only fails on genuine product behavior, not on timing noise.
            var sw = Stopwatch.StartNew();
            while (market.Status != MarketStatus.Suspended && sw.ElapsedMilliseconds < 2000)
            {
                await Task.Delay(10);
            }
        }
        else
        {
            // Let any in-flight processing settle before asserting a negative (max delay is 150ms).
            await Task.Delay(250);
        }

        Assert.That(market.Status, Is.EqualTo(expected),
            $"Market {marketId} was expected to be {expected} but was {market.Status}.");
    }

    [Then(@"market ""(.*)"" should be suspended within (\d+)ms")]
    public async Task ThenMarketShouldBeSuspendedWithinMs(string marketId, int budgetMs)
    {
        var market = _context.Markets[marketId];
        var sw = Stopwatch.StartNew();
        while (sw.ElapsedMilliseconds < budgetMs)
        {
            if (market.Status == MarketStatus.Suspended) return;
            await Task.Delay(5);
        }

        Assert.Fail($"Market {marketId} was not suspended within {budgetMs}ms (still {market.Status}).");
    }

    [Then(@"no error should have been raised")]
    public void ThenNoErrorShouldHaveBeenRaised()
    {
        Assert.That(_context.LastError, Is.Null);
    }
}
