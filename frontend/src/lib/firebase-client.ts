import { auth } from './firebase';
import { onAuthStateChanged, User, getIdToken } from 'firebase/auth';

/**
 * Get a valid ID token for the current user.
 * Forces a refresh if the token is expired or about to expire.
 */
export const getValidToken = async (): Promise<string | null> => {
    try {
        const user = auth.currentUser;
        if (!user) return null;
        // forceRefresh: true will ensure we get a fresh token if needed
        return await getIdToken(user, true);
    } catch (error) {
        console.error("Error getting valid token:", error);
        return null;
    }
};

/**
 * Setup a token refresh mechanism.
 * Firebase Auth SDK automatically handles token refresh internally,
 * effectively refreshing ~5 mins before expiration.
 * This function can be used for any additional custom interval logic if strictly required,
 * but for most standard use cases, the SDK's internal handling is sufficient.
 * We'll add a simple interval here to log/ensure validity periodically if needed.
 */
export const setupTokenRefresh = () => {
    // Firebase SDK handles basic refresh. 
    // We can set an interval to proactively ensure we have a valid token if the app requires it.
    const REFRESH_INTERVAL = 50 * 60 * 1000; // 50 minutes

    const intervalId = setInterval(async () => {
        const user = auth.currentUser;
        if (user) {
            try {
                await getIdToken(user, true);
                console.log("Token refreshed proactively.");
            } catch (e) {
                console.error("Failed to refresh token proactively:", e);
            }
        }
    }, REFRESH_INTERVAL);

    return () => clearInterval(intervalId);
};

/**
 * Subscribe to authentication state changes.
 * @param callback Function to call when auth state changes.
 * @returns Unsubscribe function.
 */
export const onAuthChange = (callback: (user: User | null) => void) => {
    return onAuthStateChanged(auth, callback);
};
