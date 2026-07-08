namespace BettingPlatform;

public sealed class Player
{
    public string PlayerId { get; init; } = "";
    public string Name { get; init; } = "";
    public string Team { get; init; } = "";
}

public enum MarketStatus
{
    Open,
    Suspended
}

public sealed class Market
{
    public string MarketId { get; init; } = "";
    public string MarketType { get; init; } = "";

    /// <summary>
    /// Players whose in-match actions can affect this market's outcome. Order matters for
    /// <see cref="MarketSuspensionService"/> today - see the comment there.
    /// </summary>
    public List<string> EligiblePlayerIds { get; init; } = new();

    public MarketStatus Status { get; set; } = MarketStatus.Open;
}

public sealed class RedCardEvent
{
    public string MatchId { get; init; } = "";
    public string PlayerId { get; init; } = "";
    public DateTimeOffset OccurredAt { get; init; } = DateTimeOffset.UtcNow;
}
