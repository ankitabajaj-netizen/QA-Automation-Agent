namespace BettingPlatform;

/// <summary>
/// Stand-in for the platform's real risk/trading service. This is the "system under test" -
/// intentionally small, in-process, and seeded with one realistic bug plus one realistic
/// timing hazard so the QE pipeline has something genuine to catch. See plan.md, "System under test".
/// </summary>
public sealed class MarketSuspensionService
{
    private readonly List<Market> _markets;
    private readonly HashSet<string> _processedPlayerIds = new();

    public MarketSuspensionService(List<Market> markets)
    {
        _markets = markets;
    }

    /// <summary>
    /// Models the real system: the red card is ingested immediately, but suspension is applied
    /// after a short, variable delay representing a message-bus hop to the trading layer.
    /// </summary>
    public async Task HandleRedCardAsync(RedCardEvent redCard)
    {
        if (!_processedPlayerIds.Add(redCard.PlayerId))
        {
            return; // idempotent no-op: this player's dismissal was already processed
        }

        await Task.Delay(Random.Shared.Next(0, 150));

        foreach (var market in _markets)
        {
            if (market.Status != MarketStatus.Open) continue;
            if (market.EligiblePlayerIds.Count == 0) continue;

            // PLANTED BUG: only the first entry in EligiblePlayerIds is ever checked. That's
            // correct for single-player markets (e.g. "Player to Score Anytime") but wrong for
            // multi-selection markets (e.g. "Anytime Assist Provider", "Next Card") whenever the
            // carded player isn't first in the list - those markets are silently left open.
            if (market.EligiblePlayerIds[0] == redCard.PlayerId)
            {
                market.Status = MarketStatus.Suspended;
            }
        }
    }
}
