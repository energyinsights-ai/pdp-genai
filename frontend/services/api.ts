export const api = {
  async get<T>(url: string): Promise<T> {
    return await $fetch<T>(url, {
      method: 'GET',
    })
  },

  async post<T>(url: string, data: any): Promise<T> {
    return await $fetch<T>(url, {
      method: 'POST',
      body: data,
    })
  },

  // Add other methods (put, delete, etc.) as needed
}

export default api