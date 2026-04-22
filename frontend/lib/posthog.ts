import PostHog from 'posthog-react-native'
import AsyncStorage from '@react-native-async-storage/async-storage'

const apiKey = process.env.EXPO_PUBLIC_POSTHOG_KEY as string | undefined
const host = process.env.EXPO_PUBLIC_POSTHOG_HOST
const isPostHogConfigured = !!apiKey && apiKey !== 'phc_your_project_token_here'

if (__DEV__ && !isPostHogConfigured) {
  console.warn(
    'PostHog project token not configured. Analytics will be disabled. ' +
      'Set EXPO_PUBLIC_POSTHOG_KEY in your .env file to enable analytics.'
  )
}

export const posthog = new PostHog(apiKey || 'placeholder_key', {
  host,
  disabled: !isPostHogConfigured,
  captureAppLifecycleEvents: true,
  flushAt: 20,
  flushInterval: 10000,
  customStorage: AsyncStorage,
})