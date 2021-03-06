// private sub-module defined in other files
mod quantiles;
mod zscores;


// exports identifiers from private sub-modules in the current module namespace
pub use self::quantiles::Quantiles;
pub use self::zscores::ZScores;